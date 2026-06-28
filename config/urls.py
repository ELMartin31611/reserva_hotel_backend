from django.urls import path

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView
)

from hotel_app.views import (RegistroView, PerfilView)

urlpatterns = [

    path( 'register/',  RegistroView.as_view(), name='register' ),

    path( 'login/', TokenObtainPairView.as_view(), name='login' ),

    path( 'token/refresh/',TokenRefreshView.as_view(), name='token_refresh' ),

    path( 'perfil/',PerfilView.as_view(),name='perfil' ),
]