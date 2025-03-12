# routing/views.py
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required
def map_view(request):
    return render(request, 'routing/map.html') 

import json
import numpy as np
from django.contrib.gis.geos import Point
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from shapely import wkb
from shapely.geometry import mapping
from tensorflow.keras.models import load_model

# Cargar el modelo y los parámetros de normalización
MODEL_PATH = "/opt/sergio/EVALUATION/lstm_travel_time_global_multi_feature_final.keras"
model = load_model(MODEL_PATH)
mean_vals = np.load("/opt/sergio/EVALUATION/mean_vals.npy")
std_vals = np.load("/opt/sergio/EVALUATION/std_vals.npy")
target_idx = 0
target_mean = mean_vals[target_idx]
target_std = std_vals[target_idx]

@login_required
@method_decorator(csrf_exempt, name='dispatch')
class RoutingView(APIView):
    def post(self, request, format=None):
        # Obtener origen y destino
        origen_data = request.data.get('origen')
        destino_data = request.data.get('destino')
        if not origen_data or not destino_data:
            return Response({"error": "Se requieren coordenadas de origen y destino."}, status=400)
        
        # Usar 'lng' en lugar de 'lon'
        origen_point = Point(origen_data['lng'], origen_data['lat'])
        destino_point = Point(destino_data['lng'], destino_data['lat'])
        
        with connection.cursor() as cursor:
            # 1. Encontrar el nodo más cercano al origen
            cursor.execute("""
                SELECT source 
                FROM links_noded
                ORDER BY wkb_geometry <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                LIMIT 1;
            """, [origen_point.x, origen_point.y])
            row = cursor.fetchone()
            if not row:
                return Response({"error": "No se encontró nodo cercano al origen."}, status=400)
            source_node = row[0]
            
            # 2. Encontrar el nodo más cercano al destino
            cursor.execute("""
                SELECT target
                FROM links_noded
                ORDER BY wkb_geometry <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                LIMIT 1;
            """, [destino_point.x, destino_point.y])
            row = cursor.fetchone()
            if not row:
                return Response({"error": "No se encontró nodo cercano al destino."}, status=400)
            target_node = row[0]
            
            # 3. Ejecutar la consulta de enrutamiento con pgr_dijkstra
            query = """
                SELECT route.seq,
                       route.node,
                       route.edge,
                       route.cost,
                       ST_AsBinary(ln.wkb_geometry) AS geom
                FROM pgr_dijkstra(
                    'SELECT id, source, target, ST_Length(wkb_geometry::geography) AS cost FROM links_noded'::text,
                    %s::integer,
                    %s::integer,
                    false::boolean
                ) AS route
                JOIN links_noded ln
                   ON route.edge = ln.id
                ORDER BY route.seq;
            """
            cursor.execute(query, [source_node, target_node])
            results = cursor.fetchall()
            
            features = []
            total_cost = 0
            for seq, node, edge, cost, geom_wkb in results:
                total_cost += cost
                geom = wkb.loads(geom_wkb.tobytes())
                features.append({
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": {"seq": seq, "node": node, "edge": edge, "cost": cost}
                })
            
            route_geojson = {
                "type": "FeatureCollection",
                "features": features
            }
        
        # 4. Obtener la secuencia de features del request (si se envía)
        features_input = request.data.get("features")
        if features_input is None:
            # Si no se envía, usamos datos hardcodeados (como ejemplo)
            sample_input = np.array([
                [5.1, 40.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.0, 41.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.2, 39.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.1, 40.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.0, 42.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.2, 40.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.1, 41.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.1, 40.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.0, 40.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.2, 40.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.1, 41.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1],
                [5.0, 40.0, 0.0, 1.0, 0.1, 0.9, 0.2, 0.8, 0, 60, 0.1]
            ])
        else:
            # Convertir la entrada a un array de NumPy
            sample_input = np.array(features_input, dtype=np.float32)
            if sample_input.ndim == 1 or (sample_input.ndim == 2 and sample_input.shape[0] == 1):
                # Si se envía un solo intervalo (11 valores), replicarlo 12 veces
                sample_input = np.tile(sample_input, (12, 1))
            elif sample_input.shape[0] < 12:
                # Si se envían menos de 12 intervalos, replicar el último hasta llegar a 12
                while sample_input.shape[0] < 12:
                    sample_input = np.vstack([sample_input, sample_input[-1]])
            elif sample_input.shape[0] > 12:
                # Si se envían más de 12, tomar solo los primeros 12
                sample_input = sample_input[:12, :]

        # Normalizar la secuencia usando los parámetros de normalización
        sample_input_norm = (sample_input - mean_vals) / std_vals
        sample_input_norm = np.expand_dims(sample_input_norm, axis=0)  # Forma final: (1, 12, 11)
        
        try:
            pred_norm = model.predict(sample_input_norm)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        # Desnormalizar e invertir la transformación logarítmica
        pred_denorm = pred_norm[0,0] * target_std + target_mean
        pred_time = float(np.expm1(pred_denorm))  # en segundos
        
        return Response({
            "route": route_geojson,
            "prediccion": pred_time
        })

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/api/map/')  # Redirige a mapa.html tras login exitoso
        else:
            return render(request, "login.html", {"error": "Usuario o contraseña incorrectos"})

    return render(request, "routing/login.html")
@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect("login")  # Redirige a login tras salir
@login_required
@csrf_exempt
def blank_view(request):
    return render(request, "routing/blank.html")  # Django buscará en "routing/templates/"