"""Django admin customization"""

from django.contrib import admin 
#The UserAdmin is the default django authentication system, define it as BaseUserAdmin because we dont want conflict with UserAdmin which is the name of our user. 
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
#Import from models, todos los models que queremos poner en django admin. 
from core import models
from django.utils.translation import gettext_lazy as _ #To translate, we use _ because it is short, but could be any name.


class UserAdmin(BaseUserAdmin): 
    """Define the admin pages for users"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}), 
        ( 
            _('Permissions'), 
            {
                'fields': (
                    'is_active', 
                    'is_staff', 
                    'is_superuser'
                )
            }
        ), 
        ( _('Important dates'), {'fields' : ('last_login', )}),
    )
    #Make field read only. 
    readonly_fields = ['last_login'] 
    add_fieldsets = (
        (None, {
            'classes': ('wide',), # this is to add css classes, it makes the text look better. 
            #En fields pasamos cuales fields queremos moestrar y obtener de la pagina. 
            'fields':(
                'email', 
                'password1', 
                'password2', 
                'name', 
                'is_active', 
                'is_staff', 
                'is_superuser'
            )
        }),
    )



#Here we register the model to be displayed in the django admin page. 
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
