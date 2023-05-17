"""
Tests for tags API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse 
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail""" 
    return reverse('recipe:tag-detail', args=[tag_id])
    


def create_user(email='test@example.com', password='pass12345'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase): 
    """Test unauthenticated API requests"""
    
    def setUp(self): 
        self.client = APIClient()
        
        
    def test_auth_required(self): 
        """test auth is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase): 
    """Test authenticated API requests"""
    
    
    def setUp(self): 
        #We create user
        self.user = create_user()
        #We create a client
        self.client = APIClient()
        #We authenticate the user in the client. 
        self.client.force_authenticate(self.user)
        
        
    def test_retrieve_tags(self): 
        """Test retrieving a list of tags"""
        #We create many tags so that we are able to obtain a list of them. 
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        
        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        
        serializer = TagSerializer(tags, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_tags_limited_to_user(self): 
        """Test list of tags is limited to authenticated user"""
        #Another user
        user2 = create_user(email='user2@example.com')
        #We created a tag for that other user. 
        Tag.objects.create(user=user2, name='Fruity')
        #We create a tag using the authenticated user. 
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        
        #We get a list of tags
        res = self.client.get(TAGS_URL)
        
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        #We are expected to see only one tag, because it is the tag that belongs to the specific user. We created one for each user in this test. 
        self.assertEqual(len(res.data), 1)
        #We check that tag name and the id from the RESULT is the same as the one we created for the authenticated user. 
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
        
        
    
    def test_update_tag(self): 
        """Test updating a tag"""
        
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {
            'name': 'Dessert'
        }
        
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        
        
        self.assertEqual(tag.name, payload['name'])
        
        
    def test_deleted_tag(self): 
        """tes delete tag"""
        
        """We create a new tag for this user"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        """We create a new url for the delete action."""
        url = detail_url(tag.id)
        """We make the DELETE request"""
        res = self.client.delete(url)
        
        """We validate the response is successful with no content returned"""
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        """We get a list od tags for this user, (it should be empty after deleting since we only created one for the user in this test)"""
        tags = Tag.objects.filter(user=self.user)
        """We want to check that the list of tags does not exist"""
        self.assertFalse(tags.exists())
        
        
        