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
		ordering = ["date"]
		verbose_name = "reservation"
	
	def __str__(self):
		return self.customer.instance.name
		
	
