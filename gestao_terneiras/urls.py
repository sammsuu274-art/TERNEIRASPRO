from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('animais/', include('animais.urls', namespace='animais')),
    path('eventos/', include('eventos.urls', namespace='eventos')),
    path('programas/', include('programas.urls', namespace='programas')),
    path('config/', include('config_tecnica.urls', namespace='config_tecnica')),
    # Dashboard como página inicial
    path('', include('core.urls_dashboard')),
    path('dashboard/', include('core.urls_dashboard')),
    path('core/', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
