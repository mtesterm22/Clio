# Modify clio/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # Add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    
    # Keep your other URLs
    path('', include('core.urls')),
    path('systems/', include('systems.urls')),
    path('workflows/', include('workflows.urls')),
    path('scripts/', include('scripts.urls')),
    path('planning/', include('planning.urls')),
    path('boards/', include('boards.urls', namespace='boards')),
    
    # Keep this after the explicit login view
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)