"""
Tests for recipe API
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer, 
    RecipeDetailSerializer,
)



RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id): 
    """Create and return a recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])





def create_recipe(user, **params): 
    """Create and return a sample recipe"""
    
    """We define a dictionary with default values"""
    defaults = {
        'title' : 'Sample title', 
        'time_minutes' : 22, 
        'price' : Decimal('5.25'), 
        'description': 'Sample description', 
        'link' : 'http://example.com/recipe.pdf', 
    }
    
    """Here we update any value that comes in the **params, if it brings no new value then if will stay with the defaul values."""
    defaults.update(params)
    
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase): 
    """Test unauthenticated API requests"""
    
    """Test Client"""
    def setUp(self): 
        self.client = APIClient()
        
    def test_auth_required(self): 
        """Test auth is required to call API"""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
    
class PrivateRecipeAPITests(TestCase): 
    """Test authenticated API requests"""
    
    def setUp(self): 
        #Test API Client
        self.client = APIClient()
        #Create user
        self.user = get_user_model().objects.create_user(
            'user@example.com', 
            'testpass12345', 
        )
        #Authenticate user
        self.client.force_authenticate(self.user)
    
    
    def test_retriee_recipes(self): 
        """Test retrieving a list of recipes"""
        
        """We create 2 recipes, so now we have more than 1"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        """Request to the API, We request the list of recipes. """
        res = self.client.get(RECIPES_URL)
        
        """We get the list from the db, ordered by id de forma ascendente"""
        recipes = Recipe.objects.all().order_by('-id')
        
        #?? We passed the recipes to the serializer, the many=True we are telling that we are going to obtain or expect a list of objetcs.
        serializer = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    
    def test_recipe_list_limited_to_user(self): 
        """Test list of recipes is limited to authenticated user"""
        
        other_user = get_user_model().objects.create_user(
            'other@example.com', 
            'password123'
        )
        
        #Not authenticated user
        create_recipe(user=other_user)
        #Authenticated user
        create_recipe(user=self.user)
        
        #We get a list of recipes, we should see only recipes for the authenticated user. 
        res = self.client.get(RECIPES_URL)
        
        #We get recipes for the authenticated user from the db
        recipes = Recipe.objects.filter(user =self.user)
        
        #We pass it trhough the serializer.
        serializer = RecipeSerializer(recipes, many=True)
        
        
        #Comparison.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
        
    def test_get_recipe_detail(self): 
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)
        #We create the url with an specific id provided for the details.
        url = detail_url(recipe.id)
        #We GET the object usgin the URL. 
        res = self.client.get(url)
        
        #We pass it trhough the serializer
        serializer = RecipeDetailSerializer(recipe)
        #We compare the result.
        self.assertEqual(res.data, serializer.data)
        
        
    def test_create_recipe(self): 
        """Test creating a recipe"""
        
        payload = {
            'title' : 'Sample recipe title', 
            'time_minutes' : 30, 
            'price' : Decimal('9.99'), 
        }
        
        #Method POST, we create a new recipe and it is stored in res.
        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get( id = res.data['id'])
        
        """k means key, v means value, so for example k will be the 'title' and v will be 'Sample recipe title'
        What this loop does is compare the key attribute and value from the payload, to the object extracted from the db stored in recipe
        """
        for k, v in payload.items(): 
            self.assertEqual(getattr(recipe, k), v)
            
        self.assertEqual(recipe.user, self.user)
    
        