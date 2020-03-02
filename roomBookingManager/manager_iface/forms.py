from django import forms 
from django.utils.safestring import mark_safe
#from .models import Room

class RoomCreationForm(forms.Form):
	
	room_no = forms.CharField(max_length=10, label="Room No.")  
	advance_period = forms.IntegerField(label=mark_safe("Max. days of <br /> advance booking"))
	# Customer can book the room anytime between this advance_period and just before the slot
	description = forms.CharField(max_length=200,required=False)
	
class SlotCreationForm(forms.Form):
	
	room = forms.ChoiceField(label="Room No.",
							required=True,
							choices=tuple(),
							)
	# null values will be handled using the form. Used here as a syntactical placeholder
	start_time = forms.TimeField(label=mark_safe("Start Time<br />(Eg. 11:30 am)"), 
								required=True,
								widget=forms.TextInput(attrs={'type':'time','min':'00:00','max':'23:59'})
								)
	end_time = forms.TimeField(label=mark_safe("End Time<br />(Eg. 11:30 pm)"), 
								required=True,
								widget=forms.TextInput(attrs={'type':'time','min':'00:00','max':'23:59'})
								)
								
								#tuple(zip(Room.objects.all(),map(str,Room.objects.all())))
								
							

