"""
Serializers for recipe APIs
"""



from rest_framework import serializers
from core.models import Recipe 


class RecipeSerializer(serializers.ModelSerializer): 
    """Serializer for recipes"""
    
    
    class Meta: 
        model = Recipe
        fields =['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']
        
class RecipeDetailSerializer(RecipeSerializer): 
    """Serializer for recipe detail view"""
    """We base it from the RecipeSerializer because it is an extesion of that class, we need everything from it and add a few more details"""
    
    """We base it from the RecipeSerializer meta class because we want the values that Meta class has
    We want the fields it already has to add a few extra ones, like description for example. 
    """
    class Meta(RecipeSerializer.Meta): 
        fields = RecipeSerializer.Meta.fields + ['description']
        