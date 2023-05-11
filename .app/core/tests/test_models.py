"""Test for models"""

from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self): 
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email = email, 
            password = password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalized(self): 
        """Test email is normalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'], 
            ['Test2@Example.com', 'Test2@example.com'], 
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'], 
            ['test4@example.COM', 'test4@example.com']
            
        ]
        
        for email, expected in sample_emails: 
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)
            
    def test_new_user_without_email_error(self): 
        """Test that creating  a user without email raises an error"""
        """We want to raise a Value error, in this case an incorrect email address."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123') 
            
            
    def test_create_superuser(self): 
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            'test@example.com', 
            'test123'
        )
        #is_superuser is a field provided by PermissionsMixin
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
       
    #Comment added to main branch code from PC. Modified 
