from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Define login with explicit template
    path('accounts/login/', 
         auth_views.LoginView.as_view(template_name='registration/login.html'), 
         name='login'),
    
    # App URLs - make sure core.urls is last to avoid conflicts
    path('systems/', include('systems.urls')),
    path('workflows/', include('workflows.urls')),
    path('scripts/', include('scripts.urls')),
    path('planning/', include('planning.urls')),
    path('boards/', include('boards.urls', namespace='boards')),
    path('', include('core.urls')),
]