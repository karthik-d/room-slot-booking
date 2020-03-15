from django.test import TestCase
from customer_iface.forms import SlotFindForm
from datetime import datetime, timedelta
from customer_iface.models import Reservation, IsolatedResData
from manager_iface.models import Room, Slot
from users.models import User, Customer, Manager, EmployeeID

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
		
		
class IsoResDataTest(TestCase):
	""" IsolatedResData is an isolated database that is not linked to any other models
	through ForeignKeys, OneToOne, etc. It is used to save data permanently for a user
	about his/her reservations including cancelled ones so that a history can be maintained
	It is attached through signals to Reservation, Customer and Slot models only
	"""
	
	def setUp(self):
		""" Creating a sample User for the test set
		"""
						
		user, waste = User.objects.get_or_create(email="temp@gmail.com",password="password")
		cust, waste = Customer.objects.get_or_create(phone="9980006526", instance=user)
		user, waste = User.objects.get_or_create(email="sample@gmail.com",password="password")
		empid, waste = EmployeeID.objects.get_or_create(emp_id="MAN002", emp_type="manager")
		manager, waste = Manager.objects.get_or_create(emp_id=empid, instance=user, phone="9980006526")
		room, watse = Room.objects.get_or_create(manager=manager, room_no='C2', advance_period=200)
		date = datetime.date(datetime.strptime("2020-5-19","%Y-%m-%d"))
		start = datetime.time(datetime.strptime("13:00","%H:%M"))
		end = datetime.time(datetime.strptime("16:00","%H:%M"))
		slot, waste = Slot.objects.get_or_create(room=room, start_time=start, end_time=end)		
		Reservation.objects.create(room=room, slot=slot, customer=cust, date=date)

	def test_is_isolatedresdata_updated_creation(self):
		""" Testing if the created Reservaytion entry, auto-created a IsoResData objects through signals
		"""		
		
		date = datetime.date(datetime.strptime("2020-5-19","%Y-%m-%d"))
		start = datetime.time(datetime.strptime("13:00","%H:%M"))
		query = IsolatedResData.objects.filter(room_no='C2', date=date, start_time=start)
		self.assertTrue(len(list(query))==1)    

	def test_is_isolatedresdata_updated_change_slot_time(self):
		""" When slot timings are modified, IsoResData should also reflect this
		happens through signals attached to save() of slot
		"""		
				
		date = datetime.date(datetime.strptime("2020-5-19","%Y-%m-%d"))
		start = datetime.time(datetime.strptime("13:00","%H:%M"))
		new_time = datetime.time(datetime.strptime("14:00","%H:%M"))
		slot = Slot.objects.get(room__room_no='C2', start_time=start)	
		slot.start_time = new_time
		slot.save(old_start_time=start, room_no='C2')
		query = IsolatedResData.objects.filter(room_no='C2', date=date, start_time=new_time)
		self.assertTrue(len(list(query))==1)   
		
	def test_is_isolatedresdata_updated_cancelled(self):
		""" Deleting a reservation invokes a signal to 
		set status to cancelled for its isoresdata if related, checking for this test...
		"""		
		
		date = datetime.date(datetime.strptime("2020-5-16","%Y-%m-%d"))   
		start = datetime.time(datetime.strptime("14:00","%H:%M"))	# New Saved Time
		cust = Customer.objects.get(instance__email="temp@gmail.com")	
		room = Room.objects.get(room_no='C2')		
		slot = Slot.objects.create(room=room, start_time=start)
		Reservation.objects.create(room=room, slot=slot, customer=cust, date=date) #CREATING ANOTHER RESERVATION
		res = Reservation.objects.get(room=room, slot=slot, date=date) 
		res.delete()
		query = IsolatedResData.objects.filter(room_no='C2', date=date, start_time=start)
		self.assertTrue(query[0].status=="Cancelled") 
		
	def test_is_isolatedresdata_updated_delete_customer(self):
		""" Deleting a customer user, deletes his reservation through model cascading 
		and further invokes a signal to delete isoresdata if related, checking for this test...
		"""		
		
		date = datetime.date(datetime.strptime("2020-5-19","%Y-%m-%d"))
		start = datetime.time(datetime.strptime("14:00","%H:%M"))	# New Saved Time	
		user = User.objects.get(email="temp@gmail.com")
		user.delete() # Deleting Customer User
		query = IsolatedResData.objects.filter(room_no='C2', date=date, start_time=start)
		self.assertTrue(len(list(query))==0)
				
		
		
