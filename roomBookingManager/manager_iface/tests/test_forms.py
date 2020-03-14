from django.test import TestCase
from manager_iface.forms import RoomCreationForm, SlotCreationForm
from datetime import datetime, timedelta


class RoomCreationFormTest(TestCase):
	""" Class based test set for the form used for room creation by manager
	"""

	def test_room_no_length(self):
		""" Room number longer than 10 digits, must be invalid
		"""
		
		room_no = '12345678901'
		form = RoomCreationForm(data={'room_no': room_no})
		self.assertFalse(form.is_valid())     
		
	def test_room_no_empty(self):
		""" Room number being empty, must be invalid
		"""
		
		room_no = ''
		form = RoomCreationForm(data={'room_no': room_no})
		self.assertFalse(form.is_valid())     	

	def test_advperiod_is_integer(self):
		""" String as advance reservation period, must be invalid
		"""
		
		form = RoomCreationForm(data={'advance_period': "string"})
		self.assertFalse(form.is_valid())
		
		
class SlotCreationFormTest(TestCase):
	""" Class based test set for the form used for slot creation by manager
	"""

	def test_room_no_existing(self):
		""" Room number should already exist to add slots, currently the test database is empty
		"""
		
		room_no = 'C105'
		form = SlotCreationForm(data={'room_no': room_no})
		self.assertFalse(form.is_valid())     
		
	def test_start_time_valid(self):
		""" Start time must be a valid time
		"""
		
		time = "time"
		form = SlotCreationForm(data={'start_time': time})
		self.assertFalse(form.is_valid())     	

	def test_end_time_valid(self):
		""" End time must be a valid time
		"""
		
		time = "time"
		form = SlotCreationForm(data={'end_time': time})
		self.assertFalse(form.is_valid()) 		
