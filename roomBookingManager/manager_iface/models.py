from django.db import models
import datetime

class Room(models.Model):
	""" Model to store details of each room in the facility 
	"""

	room_no = models.CharField(max_length=10,primary_key=True,default="")   
	# Defined as CharField for ease of operations
	# All default values will be overriden during object creation	
	manager = models.ForeignKey("users.Manager", on_delete=models.CASCADE, null=False, default=None)
	advance_period = models.IntegerField(default=10)
	description = models.TextField(max_length=200,null=True)     # Details about a particular room
	# Manager deleted --> His rooms are deleted
	
	class Meta:
		ordering = ["room_no"]
		verbose_name = "room"
	
	def __str__(self):
		return self.room_no
	
class Slot(models.Model):
	""" Model to store details of possible slots 
	mapped to their corresponding Room instances
	"""

	room = models.ForeignKey(Room, related_name='slots', on_delete=models.CASCADE, null=True)
	# null values will be handled using the form. Used here as a syntactical placeholder
	start_time = models.TimeField(default="00:00")
	end_time = models.TimeField(default="00:00")     
	# If the customer is deleted, the room becomes available 
	# All default values will be overriden during object creation
	
	class Meta:
		ordering = ["room__room_no"]     
		verbose_name = "slot"
	
	def __str__(self):
		return self.room.room_no   
		
	def save(self, *args, **kwargs):
		try:
			self.old_start_time = kwargs.pop('old_start_time',None)
			self.room_no = kwargs.pop('room_no',None)
		except KeyError:
			pass	
		super(Slot,self).save(*args,**kwargs)
		
