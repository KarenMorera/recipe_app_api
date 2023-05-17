"""
Serializers for recipe APIs
"""



from rest_framework import serializers
from core.models import(
    Recipe, 
    Tag
)
"""We need the tag serializer on top because we are going to be doing nested serializers and we need the tag to be defined first"""
class TagSerializer(serializers.ModelSerializer): 
    """Serializer for tags"""
    
    class Meta: 
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer): 
    """Serializer for recipes"""
    """This is how we define a list of tags inside our recipe serializer they are read only"""
    tags = TagSerializer(many=True, required=False)
    class Meta: 
        model = Recipe
        fields =['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']
    
    """This is to override the method create to implement the creation of tags inside the create recipe."""
    def create(self, validated_data): 
        """The pop means that we want to delete de tags data from the variable validated data and pass it to the variable tags, kind of a 
        transfer of values, we define 'tags' and the [] are in case the tags value dont exist in that variable.
        """
        tags = validated_data.pop('tags', [])
        """This is why we do the pop, because the recipe expects only the recipe data for creation, and expects
        the tags to be created separately and later assigned to the recipe."""
        recipe = Recipe.objects.create(**validated_data)
        """This gets the authenticated user, the current user making the request that has been authenticated"""
        auth_user = self.context['request'].user
        
        for tag in tags: 
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user, 
                #The **tag is so that we pass all the fields for that tag, we could to for example name=tag['name] but that will include only the name
                **tag,
            )
            recipe.tags.add(tag_obj)
        return recipe
        
class RecipeDetailSerializer(RecipeSerializer): 
    """Serializer for recipe detail view"""
    """We base it from the RecipeSerializer because it is an extesion of that class, we need everything from it and add a few more details"""
    
    """We base it from the RecipeSerializer meta class because we want the values that Meta class has
    We want the fields it already has to add a few extra ones, like description for example. 
    """
    class Meta(RecipeSerializer.Meta): 
        fields = RecipeSerializer.Meta.fields + ['description']
        

        
        
