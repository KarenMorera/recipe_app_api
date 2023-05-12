"""
Views for the recioe APIs
"""


from rest_framework import viewsets 
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet): 
    """Model View Set is set to work directly with the model"""
    """It will create default Create, Update, Read, Delete... actions"""
    
    """View for manage recipe APIs"""
    
    serializer_class = serializers.RecipeDetailSerializer
    #Objects that are going to be managed by this API
    queryset = Recipe.objects.all()
    
    #This checks that you are authenticated to use these actions.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    """override the function get_queryset"""
    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    

    def get_serializer_class(self):
        """Return the serializer class for request
        This is to choose which serializer class is going to be used, it the action is list we need a list of objects, if not it will 
        use the Detail serializer to display the details of an specific recipe. 
        """
        
        if self.action == 'list': 
            return serializers.RecipeSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer): 
        """Create a new recipe"""
        """When we perform a creating of a recioe using the Viewset create method, this method will be called."""
        """Since it passes a serializer, it is expected that the data has been validated already"""
        """This is to assigned the authenticated user, this makes sure the correct user is assigned."""
        serializer.save(user = self.request.user)


