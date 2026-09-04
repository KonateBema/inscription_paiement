from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.contrib import admin 
from django.urls import include, path 
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [

    # Administration Django
    path("admin/", admin.site.urls),
    

    # Application de gestion
    path("", include("gestion.urls")),

    # Connexion
    path(
        "connexion/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    # Déconnexion
    path(
        "deconnexion/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]

# ========================================== # FICHIERS MEDIA EN DÉVELOPPEMENT # ==========================================#
if settings.DEBUG:
    urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT )