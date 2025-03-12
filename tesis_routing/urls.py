from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from routing.views import login_view, logout_view, blank_view  # Importar vistas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('routing.urls')),  # Mantiene las rutas de "routing"
    path('login/', login_view, name='login'),  # ✅ Ahora Django reconoce login_view
    path('logout/', logout_view, name='logout'),  # ✅ Ahora Django reconoce logout_view
    path('blank/', blank_view, name='blank'),  # ✅ Ahora Django reconoce logout_view
]

# Agregar manejo de archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)