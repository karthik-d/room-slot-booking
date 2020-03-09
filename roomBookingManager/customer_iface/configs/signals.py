from customer_iface.models import IsolatedResData
from customer_iface.utilities import new_reservation_mail, reservation_cancelled_mail, slot_modified_mail
from datetime import datetime
from django.contrib import messages

def set_iso_res_cancelled(sender, instance, **kwargs):
	""" To set status of Isolated reservation Data as Cancelled when a reservation 
	gets cancelled for any reason
	"""
	
	this_iso_res = IsolatedResData.objects.get(room_no=instance.room.room_no,
													start_time=instance.slot.start_time,
													date=instance.date) 
		
	this_iso_res.status = "Cancelled"
	this_iso_res.save()
	
	response = reservation_cancelled_mail(instance)
	
def create_iso_res(sender, instance, **kwargs):
	""" To create a new instance of Isolated Reservation data when a 
	new reservation is made
	"""

	new_iso_res = IsolatedResData()
	new_iso_res.room_no = instance.room.room_no
	new_iso_res.start_time = instance.slot.start_time
	new_iso_res.end_time = instance.slot.end_time
	new_iso_res.cust_email = instance.customer.instance.email
	new_iso_res.cust_name = instance.customer.instance.name
	new_iso_res.manager_email = instance.room.manager.instance.email
	new_iso_res.manager_name = instance.room.manager.instance.name
	new_iso_res.date = instance.date
	new_iso_res.status = "Active"
	new_iso_res.save() 
	
	response = new_reservation_mail(instance)	
		
	
def change_iso_slot(sender, instance, **kwargs):
	""" To modify the start and end time of isolated reservation data instances
	when a related slot timings are modified
	"""

	today = datetime.date(datetime.now())
	now = datetime.time(datetime.now())
	if instance.room_no != None:
		this_roomno = instance.room_no
		old_start_time = instance.old_start_time	
		affect_reserves = list(IsolatedResData.objects.filter(
														room_no=this_roomno,
														start_time=old_start_time, 
														date__gt=today,
														status="Active"
													  )|IsolatedResData.objects.filter(
													  	room_no = this_roomno,
													 	start_time=old_start_time, 
														date=today,
														start_time__gte=now,
														status="Active"
													  ))	
		for i in affect_reserves:
			i.start_time = instance.start_time
			i.end_time = instance.end_time
			i.save()
			response = slot_modified_mail(i)	# Sending a mail to each affected customer
		
	else:    # Slot is not being modified, but created, IsoResData need not be modified	
		pass
		
def delete_iso_res(sender, instance, **kwargs):
	""" To delete isolated_reservation_data corresponding to a customer
	when the customer is deleted, since all his history is not required anymore"""
	
	affected_res = IsolatedResData.objects.filter(cust_email=instance.instance.email)
	for i in affected_res:
		i.delete()   # Deleting all matching records
			
