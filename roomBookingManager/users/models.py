from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model

		
class UserManager(BaseUserManager):    
	"""Manager class for the User model, overriding the deault manager class\
	"""
	
	use_in_migrations = True
	
	def create_user(self, email, password=None, **extra_fields):
		username = None
		if not email:
			raise ValueError("Email is required")
		if not password:
			raise ValueError("Password is required")
		email = self.normalize_email(email)
		
		extra_fields.setdefault("is_staff",False)
		extra_fields.setdefault("is_superuser",False)     # Setting default values for other pre-defined fields
		
		user = self.model(email=email,**extra_fields)     # An attribute referring back to User model
		user.set_password(password)
		user.save()	
		return user
		
	def create_superuser(self, email, password=None, **extra_fields): 
		#Supply True for is_staff and is_superuser for successful creation. Acts as a potential process breaker
		
		username = None
		if not email:
			raise ValueError("Email is required")
		if not password:
			raise ValueError("Password is required")
		email = self.normalize_email(email)
		
		extra_fields.setdefault("is_staff",True)
		extra_fields.setdefault("is_superuser",True)       # Setting default values for other pre-defined fields
		
		if(extra_fields.get("is_staff") is not True):
			raise ValueError("SuperUser must be Staff")
		if(extra_fields.get("is_superuser") is not True):  # Provision to abort creation, if False explicitly specified
			raise ValueError("Error in SuperUser creation")		
		
		user = self.model(email=email,**extra_fields)     # An attribute referring back to User model
		user.set_password(password)
		user.save()	
		return user	
		

class User(AbstractBaseUser, PermissionsMixin):  # PermissionsMixin to include the permission parameters of User model
	"""Customizing/overriding the pre-defined User class
	"""
	 
	email = models.EmailField(unique=True,default=None,null = False) 
	# default=None is a syntactic placeholder, handled through forms
	name = models.CharField(max_length=20,null=True,default="")
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)  
	
	USERNAME_FIELD = "email"   # Email is used as the username
	EMAIL_FIELD = "email"
	REQUIRED_FIELDS = []       # Username and password are automatically required fields
		
	class Meta:
		ordering = ["email"]
		verbose_name = "user"
    	
	def __str__(self):
		return self.name	
		
	objects = UserManager()    # Declaring the Manager Class	
						

class Customer(models.Model):
    instance = models.OneToOneField(get_user_model(),primary_key=True,on_delete=models.CASCADE,default=None)  
    # Stores the User object
    # default=None is a syntactic placeholder. Handled using forms
    phone = models.CharField(max_length=10,null=True)
    gender = models.CharField(max_length=1,choices=(("M","Male"),("F","Female")),default="M")

    def __str__(self):
        return self.instance.name


class Manager(models.Model):
    instance = models.OneToOneField(get_user_model(),primary_key=True,on_delete=models.CASCADE,default=None)  
    # Stores the User object
    # default=None is a syntactic placeholder. Handled using forms
    phone = models.CharField(max_length=10,null=True)
    gender = models.CharField(max_length=1,choices=(("M","Male"),("F","Female")),default="M")

    def __str__(self):
        return self.instance.name

