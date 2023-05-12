"""Database models"""

from django.conf import settings
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
    

#Basic model base.
class Recipe(models.Model): 
    """Recipe Object"""
    
    """Owner of the recipe, the AUTH_USER_MODEL was defined in the setting.py file, 
    the cascade means that if we delete the user, the recipes belonging to the user will be deleted as weel. 
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete= models.CASCADE, 
    )
    
    
    title = models.CharField(max_length= 255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    
    """
    this allows for the object to return itself and the display info will be the title, if we don't specify this, it will display the id
    """
    def __str__(self):
        return self.title