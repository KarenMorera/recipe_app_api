"""Database models"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager, 
    PermissionsMixin
)

class UserManager(BaseUserManager): 
    """Manager for users"""
    """Name should be like this, create_user"""
    def create_user(self, email, password=None, **extra_fields): 
        """Create, Save and Return a new User"""
        
        if not email: 
            raise ValueError('User must have an email address.')
        
        """The extra_fields argument, is for example if we pass a name, it will be created automatically in our user and we dont need to modify this instruction to include it"""
        """When calling self.model is the same as creating a new user using User class"""
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        
        """The using is to support multiple databases"""
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, password):
        """Create a new superuser""" 
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        
        user.save(using=self._db)
        return user
        

#AbstractBaseUser contains a functionality for authentication system. 
#PermissionMixin contains functionality for the permissions and fields.
class User(AbstractBaseUser, PermissionsMixin): 
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    #Is staff is to see if user can log into admin app
    is_staff = models.BooleanField(default=True)
    
    objects = UserManager()
    
    #overriding the username field to be the email
    USERNAME_FIELD = 'email'