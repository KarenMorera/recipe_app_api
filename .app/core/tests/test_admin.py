"""Tests for the django admin modifications"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse 
from django.test import Client

class AdminSiteTests(TestCase): 
    """Tests for django admin"""
    
    """The correct syntaxis for the method should be set_up, but for some reason the UnitTest module uses it like this"""
    def setUp(self):
        """Create user and client"""
        """Django test client, allows to make http requests"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@example.com', 
            password = 'testpass123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'user@example.com', 
            password = 'testpass123', 
            name = 'Test User'
        )
        
    def test_users_list(self): 
        """Test that users are listed in page"""
        """Check this page: https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#reversing-admin-urls """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)