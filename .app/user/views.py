"""Views for the user API"""
#Handle the views in a generic way. 
from rest_framework import generics, authentication, permissions 
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import (UserSerializer, AuthTokenSerializer )

from django.contrib.auth import get_user_model

from core.models import User

class CreateUserView(generics.CreateAPIView): 
    """Create a new user in the system"""
    serializer_class = UserSerializer
    

#View provided by django rest framework
class CreateTokenView(ObtainAuthToken): 
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    
class ManageUserView(generics.RetrieveUpdateAPIView): 
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self): 
        """Retrieve and return the authenticated user"""
        return self.request.user
    

#This comment is in branch TestMerge