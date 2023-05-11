"""Serializers for user API view"""

from django.contrib.auth import (
    get_user_model, 
    authenticate
)
from django.utils.translation import gettext as _
from rest_framework import serializers


"""Serializers are to convert json into python objects, in this case we receive the data in json, validate and then convert into an object
or a Model"""
class UserSerializer(serializers.ModelSerializer): 
    """Serializer for the user object"""
    
    class Meta: 
        #We tell the django framework the fields and model we are going to pass to the serializer.
        model = get_user_model()
        #Fields provided in the request, only fields that the user would be able to modify.
        fields = ['email', 'password', 'name']
        #We are saying that the password is a write only value, and we define the minimum legth of the password. 
        #This means the user will only be able to set value of the passwordd, not get the value. 
        #Returns 400 bad request if leght is not met. 
        extra_kwargs = {'password': {'write_only': True, 'min_length' :5}}
        
    #This method only gets called if the validation is done.     
    def create(self, validated_data): 
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
    
    #We are overriding the update method
    def update(self, instance, validated_data): 
        """Update and return user """
        password = validated_data.pop('password', None)#This is as default, it is not necessary that the user updates the password
        user = super().update(instance, validated_data)
        
        if password: 
            user.set_password(password)
            user.save()
            
        return user
    
    
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user Auth token""" 
    
    email = serializers.EmailField()
    password = serializers.CharField(
        style = {'input_type' : 'password'}, 
        trim_whitespace = False, 
    )
    
    def validate(self, attrs):
        """Validate and authenticate the user"""
        #Email and password passed through the input
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = authenticate(
            request= self.context.get('request'), 
            username = email, 
            password=password, 
        )
        
        if not user: 
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs
    
    
    