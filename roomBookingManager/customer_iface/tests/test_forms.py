from django.test import TestCase
from customer_iface.forms import SlotFindForm
from datetime import datetime, timedelta

class SlotFindFormTest(TestCase):
	""" Class based test set for the form used for slot reservation by customer
	"""

	def test_search_date_in_past(self):
		""" Searching rooms in the past, must be invalid
		"""
		
		date = datetime.date(datetime.now()) - timedelta(days=1)
		form = SlotFindForm(data={'date': date})
		self.assertRaises(ValueError, form.is_valid)     # Using assertRaises as context manager

	def test_search_date_today(self):
		""" Searching rooms for today, must be valid
		"""
		
		date = datetime.date(datetime.now())
		form = SlotFindForm(data={'date': date})
		self.assertTrue(form.is_valid())
