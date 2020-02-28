from django.db import models
import datetime

class Room(models.Model):
	""" Model to store details of each room in the facility 
	"""

	room_no = models.CharField(max_length=10,primary_key=True,default="")   
	# Defined as CharField for ease of operations
	# All default values will be overriden during object creation
	advance_period = models.IntegerField(default=10)
	description = models.CharField(max_length=100,null=True)     # Details about a particular room
	
	class Meta:
		ordering = ["room_no"]
		verbose_name = "rooms"
	
	def __str__(self):
		return self.room_no
	
class AvailableSlot(models.Model):
	""" Model to store details of available slots 
	mapped to their corresponding Room instances
	"""

	room = models.ForeignKey("manager_iface.Room", on_delete=models.CASCADE, null=True)
	# null values will be handled using the form. Used here as a syntactical placeholder
	start_date = models.DateField(default=datetime.date.today)
	start_time = models.TimeField(default="00:00")
	end_date = models.DateField(default=datetime.date.today)
	end_time = models.TimeField(default="00:00")      
	# All default values will be overriden during object creation
	
	class Meta:
		ordering = ["room"]     # The instance in turen returns te room number
		verbose_name = "availbale slots"
	
	def __str__(self):
		return self.start_date       
