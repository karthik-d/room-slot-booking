from users.models import Customer
import datetime
from django.core.mail import send_mail
import configparser
from django.conf import settings
import os

def new_reservation_mail(reserve):
	config = configparser.ConfigParser()
	config.read(os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini'))
	path = os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini')
	read = config.items('DATA')
	from_ = read[0][1]
	pwd = read[1][1]
	to = reserve.customer.instance.email
    
	body = """Hey {0},\nYou have reserved a room. The details are as follows:\n\n
    Room No.: {1}\n
    Date: {2}\n
    Start Time: {3}\n
    End Time: {4}\n
    Manager: {5}\n
    Manager Email: {6}\n""" 
	name = reserve.customer.instance.name
	room_no = reserve.room.room_no
	date = reserve.date.strftime("%d-%m-%Y")
	start_time = reserve.slot.start_time
	end_time = reserve.slot.end_time
	manager = reserve.room.manager.instance.name
	man_email = reserve.room.manager.instance.email
    
	body += """\nLogin to our Room Booking website for more details"""
	body = body.format(name,room_no,date,start_time,end_time,manager,man_email)
         
	subject = "New Room Slot Reserved"
	try:
		return send_mail(subject,body,from_,[to],auth_user=from_,auth_password=pwd)
	except:
		return -1
		
def reservation_cancelled_mail(reserve):
	config = configparser.ConfigParser()
	config.read(os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini'))
	path = os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini')
	read = config.items('DATA')
	from_ = read[0][1]
	pwd = read[1][1]
	to = reserve.customer.instance.email
    
	body = """Hey {0},\nYour room reservation was cancelled. The details are as follows:\n\n
    Room No.: {1}\n
    Date: {2}\n
    Start Time: {3}\n
    End Time: {4}\n
    Manager: {5}\n 
    Manager Email: {6}\n"""
	name = reserve.customer.instance.name
	room_no = reserve.room.room_no
	date = reserve.date.strftime("%d-%m-%Y")
	start_time = reserve.slot.start_time
	end_time = reserve.slot.end_time
	manager = reserve.room.manager.instance.name
	man_email = reserve.room.manager.instance.email
    
	body += """\nIf you did not cancel it, the reason could be:\n
	1. Your Profile was deleted.\n
	2. Concerned Room was cancelled by manager.\n
	3. Concerned Slot was cancelled by manager.\n
	Contact Manager for clarifications. \nLogin to our Room Booking website to view cancellation listing"""
	body = body.format(name,room_no,date,start_time,end_time,manager,man_email)
         
	subject = "Room Slot Cancelled"
	try:
		return send_mail(subject,body,from_,[to],auth_user=from_,auth_password=pwd)
	except:
		return -1	
		
def slot_modified_mail(iso_reserve):
	config = configparser.ConfigParser()
	config.read(os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini'))
	path = os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini')
	read = config.items('DATA')
	from_ = read[0][1]
	pwd = read[1][1]
	to = iso_reserve.cust_email
    
	body = """Hey {0},\nYour room reservation timings were modified by manager. The details are as follows:\n\n
    Room No.: {1}\n
    Date: {2}\n
    New Start Time: {3}\n
    New End Time: {4}\n
    Manager: {5}\n 
    Manager Email: {6}\n"""
	name = iso_reserve.cust_name
	room_no = iso_reserve.room_no
	date = iso_reserve.date.strftime("%d-%m-%Y")
	start_time = iso_reserve.start_time
	end_time = iso_reserve.end_time
	manager = iso_reserve.manager_name
	man_email = iso_reserve.manager_email
    
	body += """\nContact Manager for clarifications. 
	\nLogin to our Room Booking website to view/cancel booking"""
	body = body.format(name,room_no,date,start_time,end_time,manager,man_email)
         
	subject = "Room Slot Timings Modified"
	try:
		return send_mail(subject,body,from_,[to],auth_user=from_,auth_password=pwd)
	except:
		return -1		
		
def send_generated_key(emp_id_inst):
	config = configparser.ConfigParser()
	config.read(os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini'))
	path = os.path.join(settings.BASE_DIR,'customer_iface','configs','data_config.ini')
	read = config.items('DATA')
	from_ = read[0][1]
	pwd = read[1][1]
	to = emp_id_inst.creator.email
    
	body = """Hey {0},\nYou generated a new employee. The details are as follows:\n\n
    Employee Type: {1}\n
    Employee ID: {2}\n"""
	name = emp_id_inst.creator.name
	typ = emp_id_inst.emp_type
	gen_id = emp_id_inst.emp_id
    
	body += """Login to our Room Booking website to view/delete employee IDs"""
	body = body.format(name, typ, gen_id)
         
	subject = "New Employee ID Generated"
	try:
		return send_mail(subject,body,from_,[to],auth_user=from_,auth_password=pwd)
	except:
		return -1										
