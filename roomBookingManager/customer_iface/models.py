from django.db import models
from users.models import Customer
import datetime

class Reservation(models.Model):
	"""Model to preserve reservation status of the network of rooms associating with a specific customer
	"""
	room = models.ForeignKey('manager_iface.Room', on_delete=models.CASCADE, null=False, default=None)
	customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE, null=False, default=None) 
	# Deletion of customer --> cancelled reservation
	date = models.DateField(default=datetime.date.today)
	slot = models.ForeignKey('manager_iface.Slot', on_delete=models.CASCADE, null=False, default=None)
	# All default values will be overriden during object creation
	
	class Meta:
		ordering = ["-date"]
		verbose_name = "reservation"
	
	def __str__(self):
		return self.customer.instance.name
		
			
class IsolatedResData(models.Model):
	""" A model that is in now manner linked to any other databases.
	TO PRESERVE LIMITED AMOUNT OF PAST DATA, EVEN IF SLOTS GET MODIFED OVER TIME, MANAGERS or CUSTOMERS GO AWAY, etc.
	This database is explicitly updated during such data-loss operations. It is accessed only for 
	knowing past data and is not relied upon for any sort of actions, except viewing
	"""
	# default=None is a syntactic placeholder, handled through forms
	room_no = models.CharField(max_length=10,default="")
	manager_email = models.EmailField(default=None,null = False) 
	manager_name = models.CharField(max_length=20,null=True,default="") 
	cust_email = models.EmailField(default=None,null = False) 
	cust_name = models.CharField(max_length=20,null=True,default="")
	date = models.DateField(default=datetime.date.today)
	start_time = models.TimeField()     #Storing in raw-form, always used in 24-hr format
	end_time = models.TimeField() 
	status = models.CharField(max_length=10, default="Active")
	
	class Meta:
		ordering = ["-date"]
		verbose_name = "isolated reservation data"
	
	def __str__(self):
		return self.room_no
			
		
	
