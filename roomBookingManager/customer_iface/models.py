from django.db import models
from users.models import Customer
import datetime

class Reservation(models.Model):
	"""Model to preserve reservation status of the network of rooms associating with a specific customer
	"""

	reservation_id = models.CharField(max_length=10,primary_key=True)
	customer = models.ForeignKey('users.Customer',on_delete=models.CASCADE) # Deletion of customer --> cancelled reservation
	start_date = models.DateField(default=datetime.date.today)
	start_time = models.TimeField(default="00:00")
	end_date = models.DateField(default=datetime.date.today)
	end_time = models.TimeField(default="00:00")      # All default values will be overriden during object creation
	
	class Meta:
		ordering = ["start_date"]
		verbose_name = "reservations"
	
	def __str__(self):
		return self.reservation_id
		
class ReservedRoom(models.Model):
	"""Model to store reserved rooms. Simply an extension of Reservations model to associate multiple roms with same
	reservation ID
	"""
	
	reservation = models.ForeignKey(Reservation,on_delete=models.CASCADE)  # Deletion of reservation --> room unreserved
	room = models.ForeignKey('manager_iface.Room',on_delete=models.CASCADE) # Deletion of room --> cancelled reservation
		
	class Meta:
		ordering = ["reservation_id"]
		verbose_name = "reserved rooms"
	
	def __str__(self):
		return self.reservation_id		
