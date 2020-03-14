from django import forms 
from django.utils.safestring import mark_safe
from datetime import datetime
from .models import Room
#from .models import Room

class RoomCreationForm(forms.Form):
	""" Class based form to accept details in order to allow a manager to
	create a new room
	"""
		
	room_no = forms.CharField(max_length=10, label="Room No.", required=True)  
	# mark_safe is used to allow HTML tags to be carried over to the template. <br /> in this case
	advance_period = forms.IntegerField(label=mark_safe("Max. days of <br /> advance booking"), required=True)
	# Customer can book the room anytime between this advance_period and just before the slot
	description = forms.CharField(max_length=200,required=False)
	
	def clean_room_no(self):
		data = self.cleaned_data['room_no']
		if(len(data)>10):
			raise ValueError("Room Number should not be longer than 10 characters")
		return data	
		
	def clean_advance_period(self):
		data = self.cleaned_data['advance_period']
		for i in str(data):
			if not i.isdigit():
				raise ValueError("Period must be an integer (in days)")	
		return data		
	
class SlotCreationForm(forms.Form):
	""" Class based view to accept details to Create a new slot for a
	particular room. This is for the manager user
	"""

	def __init__(self, *args, **kwargs):
		room_choices = kwargs.pop('choices', (()))  # Assuming no choices are available if not supplied
		if(kwargs.pop('for_modification',False)):   # Removing extra kwargs before calling base class ctor
			room_inst = kwargs.pop('room_inst')
			slot_inst = kwargs.pop('slot_inst')
			super(SlotCreationForm, self).__init__(*args, **kwargs)    # Calling base ctor to use 'fields'
			self.fields['room'].choices = [(room_inst, room_inst.room_no)]
			self.fields['room'].disabled = True
			self.fields['start_time'].initial = slot_inst.start_time.strftime("%H:%M")
			self.fields['end_time'].initial = slot_inst.end_time.strftime("%H:%M")
		else:
			super(SlotCreationForm, self).__init__(*args, **kwargs)
			self.fields['room'].choices = room_choices
	
	room = forms.ChoiceField(label="Room No.",
							required=True,
							choices=tuple(),
							)
	start_time = forms.TimeField(label=mark_safe("Start Time<br />(Eg. 11:30 am)"), 
								required=True,
								widget=forms.TextInput(attrs={'type':'time','min':'00:00','max':'23:59'})
								)
	end_time = forms.TimeField(label=mark_safe("End Time<br />(Eg. 11:30 pm)"), 
								required=True,
								widget=forms.TextInput(attrs={'type':'time','min':'00:00','max':'23:59'})
								)
	
	def clean_room(self):
		data = self.cleaned_data['room']
		try:
			Room.objects.get(room_no=data)
		except Room.DoesNotExist:
			raise ValueError("Room Must Already Exist")				
		return data		
								
	def clean_start_time(self):
		data = self.cleaned_data['start_time']
		try:
			data.strftime("%H:%M")
		except ValueError:	
			raise ValueError("Invalid Time")
		except AttributeError:                 # Occurs if a string is forciby fed to the Input Form
			raise ValueError("Invalid Time Input Format")		
		return data	 							
					
	def clean_end_time(self):
		data = self.cleaned_data['end_time']
		try:
			data.strftime("%H:%M")
		except ValueError:	
			raise ValueError("Invalid Time")
		except AttributeError:
			raise ValueError("Invalid Time Input Format")			
		return data								
								
							

