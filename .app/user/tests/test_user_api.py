"""Tests for the user API"""

from django.test import TestCase 
from django.contrib.auth import get_user_model
from django.urls import reverse 

from rest_framework.test import APIClient 
from rest_framework import status

#This will return a url. 
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params): 
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)



class PublicUserApiTests(TestCase): 
    
    def setUp(self): 
        self.client = APIClient()
        
    def test_create_success(self): 
        """Test creating a user is successful"""
        """Content that is being passed in the http request"""
        payload ={
            'email':'test@example.com', 
            'password':'testpass123', 
            'name': 'Test Name'
        }
        
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email = payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
    
    def test_user_with_email_exists_error(self): 
        """Test error returned if user with email exists"""
        payload = {
            'email' :'test@example.com', 
            'password': 'testpass123', 
            'name': 'Test Name'
        }
        create_user(**payload)
        #Send the request to the url with a payload
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_password_too_short_error(self): 
        """Test an error is returned if password less than 5 chars"""
        
        payload = {
            'email': 'test@example.com', 
            'password':'pw', 
            'name': 'Test Name'
            
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
        
    def test_create_token_for_user(self): 
        """Generates token for valid credentials"""
        user_details = {
            'name' : 'Test Name', 
            'email' : 'test@example.com', 
            'password' : 'test-user-password123' 
        }
        create_user(**user_details)
        
        #Payload sent for the authentication. 
        payload = {
            'email': user_details['email'], 
            'password': user_details['password'], 
        }        
        
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_create_token_bad_credentials(self): 
        """Test returns error if credentials returns invalid"""
        create_user(email ='test@example.com', password = 'goodpass')
        
        payload = {'email': 'test@example.com' , 'password': 'badpass'}
        
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_token_blank_password(self): 
        """Test posting a blank password returns an error"""
        payload = {'email': 'test@example.com' , 'password': ''}
        
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_user_unauthorized(self): 
        """Test authentication is required for users"""
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateUserApiTest(TestCase):
    """Test API requests that require authentication"""
    def setUp(self): 
        self.user = create_user(
            email = 'test@example.com', 
            password = 'testpass123', 
            name = 'Test Name'
        )
        
        #API Testing client provided by the rest framework
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_profile_success(self): 
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name' : self.user.name, 
            'email' : self.user.email,
        })
        
    def test_post_me_not_allowed(self): 
        """Test post is not allowed for the me endpoint"""
        """POST is disabled for me endpoint"""
        res = self.client.post(ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)   
    
    def test_update_user_profile(self): 
        """Test updating the user profile for the authenticated user"""
        payload = {
            'name': 'Updated Name', 
            'password' : 'newpassword123'
        }
        res = self.client.patch(ME_URL, payload)
        
        #We need to refresh since it does not do it automatically. 
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.password, payload['password'])
        self.assertEqual(res.status_code, status.HTTP_200_OK) 
    
    