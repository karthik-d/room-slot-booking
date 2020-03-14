from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.contrib.auth import get_user_model
		
class UserManager(BaseUserManager):    
	"""Manager class for the User model, overriding the deault manager class
	to customise the fileds and redefine the create_user and create_superuser functions
	"""
	
	use_in_migrations = True
	
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError("Email is required")
		email = self.normalize_email(email)
		
		extra_fields.setdefault("is_staff",False)
		extra_fields.setdefault("is_superuser",False)     # Setting default values for other pre-defined fields
		
		user = self.model(email=email,**extra_fields)     # An attribute referring back to User model
		user.set_password(password)
		user.save()	
		return user
		
	def create_superuser(self, email, password=None, **extra_fields): 
		#Supply True for is_staff and is_superuser for successful creation. Acts as a potential process breaker
		
		if not email:
			raise ValueError("Email is required")
		email = self.normalize_email(email)
		
		extra_fields.setdefault("is_staff",True)
		extra_fields.setdefault("is_superuser",True)       # Setting default values for other pre-defined fields
		
		if(extra_fields.get("is_staff") is not True):
			raise ValueError("SuperUser must be Staff")
		if(extra_fields.get("is_superuser") is not True):  # Provision to abort creation, if False explicitly specified
			raise ValueError("Error in SuperUser creation")		
		
		user = self.model(email=email,**extra_fields)      # An attribute referring back to User model
		user.set_password(password)
		user.save()	
		
		serial = Admin.objects.all().count() + 1		
		new_admin = Admin()                                # Update the Admin database
		new_admin.instance = user
		new_admin.admin_id = "ADM"+(str(serial).rjust(3,'0'))
		new_admin.save()
		
		admin_group = Group.objects.get(name="CustomerPrivilege")
		admin_group.user_set.add(user)
		
		return user	
		

class User(AbstractBaseUser, PermissionsMixin):  # PermissionsMixin to include the permission parameters of User model
	"""Customizing/overriding the pre-defined User class, to facilitate login by email id and store only 
	necessary fields. Uses in a one-to-one relation with the User TYpe classes like Customer, Admin, etc.
	"""
	 
	email = models.EmailField(unique=True,default=None,null = False) 
	# default=None is a syntactic placeholder, handled through forms
	name = models.CharField(max_length=20,null=True,default="")
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)  
	
	USERNAME_FIELD = "email"   # Email is used as the username
	EMAIL_FIELD = "email"
	REQUIRED_FIELDS = ["name"]       # Username and password are automatically required fields
		
	class Meta:
		ordering = ["email"]
		verbose_name = "user"
    	
	def __str__(self):
		return self.name	
		
	objects = UserManager()    # Declaring the Manager Class	
						

class Customer(models.Model):   
	""" customer model to create a database that stores details pertaining to 
	a customer type user. It has a one-to-one relation with members of the User class
	that stores name and login details - fields common to all types of users
	"""
	
	instance = models.OneToOneField(get_user_model(),primary_key=True,
									 related_name="customer", 
									 on_delete=models.CASCADE,
									 default=None)  
    # Stores the User object
    # default=None is a syntactic placeholder. Handled using forms
	phone = models.CharField(max_length=10,null=True)
	gender = models.CharField(max_length=1,choices=(("M","Male"),("F","Female")),default="M")
    
	class Meta:
		ordering = ["instance"]
		verbose_name = "customer"

	def __str__(self):
		return self.instance.name
		

class EmployeeID(models.Model):
	""" Model to store employee IDs generated so far and the admin who generated it as well as who has 
	been assigned to it. Currently Managers and admins are the only types of employees. Scenario can be extended to 
	any number of user types by altering the USER+REFIXES in the constants.py file and adding necessary user type models
	like Manager, Admin, etc
	"""
	
	emp_id = models.CharField(max_length=10, primary_key=True, default=None)  
	emp_type = models.CharField(max_length=10, null=False, default=None)
	creator = models.ForeignKey(User, related_name="id_creator", on_delete=models.CASCADE, default=None, null=True)  
	assignee = models.ForeignKey(User, related_name="id_assignee", on_delete=models.SET_NULL, default=None, null=True) 
	# If a the employee User is deleted, the ID remains unassigned, to be reused for a new employee  
	# default=None is a syntactic placeholder. Handled using forms 
	
	class Meta:
		ordering = ["emp_id"]
		verbose_name = "employee id"	

	def __str__(self):
		return self.emp_id	
				
		
class Admin(models.Model):
	""" Model to store details of "superuser" privileged user, who can generate employee ids and delete
	employees. One superuser is created explicitly, initially
	with admin ID - "ADM001". This is the BASE_ADMIN and cannot be delete. His creastor is NULL/None
	"""

	instance = models.OneToOneField(get_user_model(), 
										primary_key=True, 
										related_name='admin', 
										on_delete=models.CASCADE, 
										default=None)  
    # Stores the User object
    # default=None is a syntactic placeholder. Handled using forms
	emp_id = models.OneToOneField(EmployeeID,default=None,on_delete=models.CASCADE) # A unique key generated by another admin

	class Meta:
		ordering = ["instance"]
		verbose_name = "admin"

	def __str__(self):
		return self.instance.name  		
		

class Manager(models.Model):
	""" Manager model to create a database that stores details pertaining to 
	a manager type user. It has a one-to-one relation with members of the User class
	that stores name and login details - fields common to all types of users
	"""
	
	instance = models.OneToOneField(get_user_model(),primary_key=True,
									related_name="manager",
									on_delete=models.CASCADE,
									default=None)  
    # Stores the User object
    # default=None is a syntactic placeholder. Handled using forms
	emp_id = models.OneToOneField(EmployeeID,default=None,on_delete=models.CASCADE)   # A unique key generated by admin
	phone = models.CharField(max_length=10,null=True)
	gender = models.CharField(max_length=1,choices=(("M","Male"),("F","Female")),default="M")

	class Meta:
		ordering = ["instance"]
		verbose_name = "manager"

	def __str__(self):
		return self.instance.name
        
       
