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
    """Create and return a sample recipe, helper function"""
    
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

def create_user(**params): 
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)



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
        self.user = create_user(email= 'user@example.com', password='test123')
        #Authenticate user
        self.client.force_authenticate(self.user)
    
    
    def test_retrieve_recipes(self): 
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
        
        other_user = create_user(email ='other@example.com', password ='password123')
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
        
    def test_partial_update(self): 
        """Test partial update of a recipe, we will update a part of the object"""
        
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user = self.user, 
            title = 'Sample title', 
            link = original_link, 
        )
        
        payload = { 
            'title' : 'New Title', 
        }
        #We create a new URL by passing the ID of the recipe we just created. 
        url = detail_url(recipe.id)
        #We update the recipe object
        res = self.client.patch(url, payload)
        
        #We check that it was updated successfully
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        #We refresh object from the database to refresh changes.
        recipe.refresh_from_db()
        #We check that the title was updated
        self.assertEqual(recipe.title, payload['title'])
        #We check that the link is still the original link with which the object was created. 
        self.assertEqual(recipe.link, original_link)
        #We check that the user owner of the recipe is the same as the one doing the update.
        self.assertEqual(recipe.user, self.user)
        
    def test_full_update(self): 
        """Test full update of recipe"""
        
        #Create sample recipe
        recipe = create_recipe(
            user = self.user, 
            title = 'Sample title recipe', 
            link = 'https://example.com/recipe.pdf',
            description = 'Description of a recipe.',
        )
        
        #Create payload that is going to modify the recipe. 
        payload = {
            'title' : 'Sample updated title', 
            'link' : 'https://example.com/updated_recipe.pdf', 
            'description' : 'Updated Description',
            'time_minutes' : 10, 
            'price' : Decimal('4.45'), 
        }
        
        #Create URL using the recipe.id
        url = detail_url(recipe.id)
        #Method PUT
        res = self.client.put(url, payload)
        
        #Verify that the result is 200 OK
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        #Refresh object
        recipe.refresh_from_db()
        
        #Check payload values against recipe object, verify that they were successfully updated. 
        for k,v in payload.items(): 
            self.assertEqual(getattr(recipe, k) , v)
            
        #Check that we are using the correct user still. 
        self.assertEqual(recipe.user, self.user)
    
    
    def test_update_user_returns_error(self): 
        """test changing the recipe user, results in an error."""
        
        new_user = create_user(email = 'test@example.com', password= 'testpass123')
        recipe = create_recipe(user=self.user)
        
        payload = {
            'user' : new_user.id
        }
        
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        
        recipe.refresh_from_db()
        
        self.assertEqual(recipe.user, self.user)
        
    def test_delete_recipe(self): 
        """Test Delete a recipe successful"""
        
        recipe = create_recipe(user = self.user)
        
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        
        #Returns 204 no content because there is nothing to return. 
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        #We verify the recipe does not exist
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
        
        
    def test_delete_recipe_other_users_recipe_error(self): 
        """Test trying to delete another user's recipe gives an error"""
        
        new_user = create_user(email = 'user2@example.com', password='tes1234')
        recipe = create_recipe(user=new_user)
        
        url = detail_url(recipe.id)
        #Current user is going to delete the recipe
        res = self.client.delete(url)
        
        #Result should be a 404 not found because it is not that user's recipe
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        #We verify that the recipe still exists after the attempt of deletion.
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())