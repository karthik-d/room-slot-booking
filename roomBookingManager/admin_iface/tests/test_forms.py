from django.test import TestCase
from users.forms import CustomerRegisterForm, ManagerRegisterForm, AdminRegisterForm, PasswordChangeForm
from users.views import RegisterCustomer, RegisterManager, RegisterAdmin
from users.models import User, Manager, Admin, EmployeeID
from datetime import datetime, timedelta


class CustomerRegisterFormTest(TestCase):
	""" Class based test set for the form used for signup of a new customer
	"""
	
	def setUp(self):
		""" Creating a sample User for the test set
		"""
		
		User.objects.create_user(email="temp@gmail.com",password="password")
		EmployeeID.objects.create(emp_id="MAN001",creator=None,emp_type="manager")
	
	def test_email_exists(self):
		""" Entered email id must not already exist
		"""
		
		email = "temp@gmail.com"
		form = CustomerRegisterForm(data={'email':email})
		self.assertTrue(RegisterCustomer().email_exits(email))  # Invoking same test function that is used during 
																# customer registration, testing its output
																# returns True implying email already exists and
																# process will be terminated in actual implementation		

	def test_name_with_digits(self):
		""" Customer Name should not have digits
		"""
		
		name = 'sadam12a'
		form = CustomerRegisterForm(data={'name': name})
		self.assertRaises(ValueError, form.is_valid)     
		
	def test_email_id_valid(self):
		""" Entered email ID must be a valid one
		"""
		
		email = 'Kiran.C@g'
		form = CustomerRegisterForm(data={'email': email})
		self.assertRaises(ValueError, form.is_valid)     	

	def test_mobileno_is_digitonly(self):
		""" Entered mobile no must be only numbers
		"""
		
		num = "98765abc"
		form = CustomerRegisterForm(data={'mobile': num})
		self.assertRaises(ValueError, form.is_valid)   
		
	def test_mobileno_length_less(self):
		""" Entered mobile no is exactly 10 digits, not less
		"""
		
		num = "98765"
		form = CustomerRegisterForm(data={'mobile': num})
		self.assertRaises(ValueError, form.is_valid) 
		
	def test_mobileno_length_more(self):
		""" Entered mobile no is exactly 10 digits, not more
		"""
			 
		num = "98765432123455"
		form = CustomerRegisterForm(data={'mobile': num})
		self.assertFalse(form.is_valid())  
		
	def test_gender_valid(self):
		""" Gender must be chosen as M or F only
		"""
			 
		gen = "string"
		form = CustomerRegisterForm(data={'gender': gen})
		self.assertFalse(form.is_valid())  
		
	def test_short_password(self):
		""" Password must be atleast 6 characters
		"""
			 
		pwd = "short"
		form = CustomerRegisterForm(data={'password': pwd})
		self.assertRaises(ValueError, form.is_valid) 
		
	def test_long_password(self):
		""" Password must be at most 20 characters
		"""
			 
		pwd = "long"*6
		form = CustomerRegisterForm(data={'password': pwd})
		self.assertFalse(form.is_valid()) 	 	
		
	
class ManagerRegisterFormTest(TestCase):
	""" Class based test set for the form used for signup of a new customer
	"""
	
	def setUp(self):
		""" Creating a sample User, manager and employee id for the test set
		"""
		
		user = User.objects.create_user(email="temp@gmail.com",password="password",name="temp")
		emp_id = EmployeeID.objects.create(emp_id="MAN001",creator=None,emp_type="manager")
		manager = Manager.objects.create(instance=user,emp_id=emp_id,phone='9876543210',gender='M')
	
	def test_email_exists(self):
		""" Entered email id must not already exist
		"""
		
		email = "temp@gmail.com"
		form = CustomerRegisterForm(data={'email':email})
		self.assertTrue(RegisterCustomer().email_exits(email))  # Invoking same test function that is used during 
																# customer registration, testing its output
																# returns True implying email already exists and
																# process will be terminated in actual implementation

	def test_name_with_digits(self):
		""" Customer Name should not have digits
		"""
		
		name = 'sadam12a'
		form = ManagerRegisterForm(data={'name': name})
		self.assertRaises(ValueError, form.is_valid)     
		
	def test_email_id_valid(self):
		""" Entered email ID must be a valid one
		"""
		
		email = 'Kiran.C@g'
		form = ManagerRegisterForm(data={'email': email})
		self.assertFalse(form.is_valid())     	

	def test_mobileno_is_digitonly(self):
		""" Entered mobile no must be only numbers
		"""
		
		num = "98765abc"
		form = ManagerRegisterForm(data={'mobile': num})
		self.assertRaises(ValueError, form.is_valid)   
		
	def test_mobileno_length_less(self):
		""" Entered mobile no is exactly 10 digits, not less
		"""
		
		num = "98765"
		form = ManagerRegisterForm(data={'mobile': num})
		self.assertRaises(ValueError, form.is_valid) 
		
	def test_mobileno_length_more(self):
		""" Entered mobile no is exactly 10 digits, not more
		"""
			 
		num = "98765432123455"
		form = ManagerRegisterForm(data={'mobile': num})
		self.assertFalse(form.is_valid())  
		
	def test_gender_valid(self):
		""" Gender must be chosen as M or F only
		"""
			 
		gen = "string"
		form = ManagerRegisterForm(data={'gender': gen})
		self.assertFalse(form.is_valid())  
		
	def test_short_password(self):
		""" Password must be atleast 6 characters
		"""
			 
		pwd = "short"
		form = ManagerRegisterForm(data={'password': pwd})
		self.assertRaises(ValueError, form.is_valid) 
		
	def test_long_password(self):
		""" Password must be at most 20 characters
		"""
			 
		pwd = "long"*6
		form = ManagerRegisterForm(data={'password': pwd})
		self.assertFalse(form.is_valid())  	
		
	def test_empid_exist(self):
		"""Entered employee ID must be already be created by admin
		"""
		
		empid = "MAN001"
		form = ManagerRegisterForm(data={'emp_id':EmployeeID.objects.get(emp_id=empid)})
		self.assertTrue(RegisterManager().id_exits(empid)) 		# Invoking same test function that is used during 
																# customer registration, testing its output
																# returns True implying email already exists and
																# process will be terminated in actual implementation
		
	def test_empid_valid(self):
		"""Entered employee ID must be valid i.e of same employee type
		"""
		
		empid = "MAN001"
		form = ManagerRegisterForm(data={'emp_id':EmployeeID.objects.get(emp_id=empid)})
		self.assertTrue(RegisterManager().id_valid(empid)) 		# Invoking same test function that is used during 
																# customer registration, testing its output
																# returns True implying email already exists and
																# process will be terminated in actual implementation
																
class AdminRegisterFormTest(TestCase):
	""" Class based test set for the form used for signup of a new Admin
	"""
	
	def setUp(self):
		""" Creating a sample User, admin and employee id for the test set
		"""
		
		user = User.objects.create_user(email="temp@gmail.com",password="password",name="temp")
		emp_id = EmployeeID.objects.create(emp_id="ADM004",creator=None,emp_type="admin")
		admin = Admin.objects.create(instance=user,emp_id=emp_id)
	
	def test_email_exists(self):
		""" Entered email id must not already exist
		"""
		
		email = "temp@gmail.com"
		form = AdminRegisterForm(data={'email':email})
		self.assertTrue(RegisterAdmin().email_exits(email))  # Invoking same test function that is used during 
																# Admin registration, testing its output
																# returns True implying email already exists and
																# process will be terminated in actual implementation

	def test_name_with_digits(self):
		""" Admin Name should not have digits
		"""
		
		name = 'sadam12a'
		form = AdminRegisterForm(data={'name': name})
		self.assertRaises(ValueError, form.is_valid)     
		
	def test_email_id_valid(self):
		""" Entered email ID must be a valid one
		"""
		
		email = 'Kiran.C@g'
		form = AdminRegisterForm(data={'email': email})
		self.assertFalse(form.is_valid()) 
		
	def test_short_password(self):
		""" Password must be atleast 6 characters
		"""
			 
		pwd = "short"
		form = AdminRegisterForm(data={'password': pwd})
		self.assertRaises(ValueError, form.is_valid) 
		
	def test_long_password(self):
		""" Password must be at most 20 characters
		"""
			 
		pwd = "long"*6
		form = AdminRegisterForm(data={'password': pwd})
		self.assertFalse(form.is_valid())  	
		
	def test_empid_exist(self):
		"""Entered employee ID must be already be created by admin
		"""
		
		empid = "ADM004"
		form = AdminRegisterForm(data={'emp_id':EmployeeID.objects.get(emp_id=empid)})
		self.assertTrue(RegisterAdmin().id_exits(empid)) 		# Invoking same test function that is used during 
																# admin registration, testing its output
																# returns True implying email already exists and
																# process will be terminated in actual implementation
		
	def test_empid_valid(self):
		"""Entered employee ID must be valid i.e of same employee type
		"""
		
		empid = "ADM004"
		form = AdminRegisterForm(data={'emp_id':EmployeeID.objects.get(emp_id=empid)})
		self.assertTrue(RegisterAdmin().id_valid(empid)) 		# Invoking same test function that is used during 
																# admin registration, testing its output
																# returns True implying email already exists and
																# process will be terminated in actual implementation	    																	
class PasswordChangeFormTest(TestCase):
	""" Class based test set for the form used changing a user's password
	"""
	
	def test_short_password(self):
		""" Password must be atleast 6 characters
		"""
			 
		pwd = "short"
		form = PasswordChangeForm(data={'password': pwd})
		self.assertRaises(ValueError, form.is_valid) 
		
	def test_long_password(self):
		""" Password must be at most 20 characters
		"""
			 
		pwd = "long"*6
		form = PasswordChangeForm(data={'password': pwd})
		self.assertFalse(form.is_valid())  	
	

