from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class CustomerRegisterForm(forms.Form):
	"""Class based form to define fields for accepting Customer details
	to create a customer class and the corresponding record in the User class
	"""
    
	name = forms.CharField(max_length=20,label="Full Name",required=True)
	# Made as a char field becuase email validation is done using a much more strict validate_email function below
	email = forms.CharField(max_length=45,widget=forms.EmailInput,label="Email Address",required=True)
	password = forms.CharField(max_length=20,widget=forms.PasswordInput,label="Password",required=True)
	repwd = forms.CharField(max_length=20,widget=forms.PasswordInput,label="Confirm Password",required=True)    
	mobile = forms.CharField(max_length=10,label="Mobile Number",required=True)
	gender = forms.ChoiceField(choices=(("M","Male"),("F","Female")),label="Gender")

	def clean_name(self):
		data = self.cleaned_data['name']
		for k in data:
			if k.isdigit():
				raise ValueError("Name cannot contain digits")
		return data
		
	def clean_email(self):
		data = self.cleaned_data['email']
		try:
			validate_email(data)
		except ValidationError:
			raise ValueError("Enter a Valid Email ID")
		return data			

	def clean_password(self):
		data = self.cleaned_data['password']
		if len(data)<6:
			raise ValueError("Password Should Be Atleast 6 Characters")
		if len(data)>20:
			raise ValueError("Password Should Not Be More Than 20 Characters")
		return data    

	def clean_mobile(self):
		data = self.cleaned_data['mobile']
		if len(data)!=10:
			raise ValueError("Mobile Number must be 10 digits")
		for k in data:
			if not k.isdigit():
				raise ValueError("Only Numbers Allowed in Mobile No")
			return data
			
	def clean_gender(self):			  
		data = self.cleaned_data['gender']
		if(data not in ['M','F']):
			raise ValueError("Gender must be M/F")
		return data		
    
class ManagerRegisterForm(forms.Form):
	"""Class based form to define fields for accepting Manager details
	to create a customer class and the corresponding record in the User class
	"""
    
	name = forms.CharField(max_length=20,  label="Full Name", required=True)
	emp_id = forms.CharField(max_length=10, label="Assigned Employee ID", required=True)
	email = forms.CharField(max_length=45, widget=forms.EmailInput, label="Email Address", required=True)
	password = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Password", required=True)
	repwd = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Confirm Password",required=True)    
	mobile = forms.CharField(max_length=10, label="Mobile Number", required=True)
	gender = forms.ChoiceField(choices=(("M","Male"),("F","Female")), label="Gender")

	def clean_name(self):
		data = self.cleaned_data['name']
		for k in data:
			if k.isdigit():
				raise ValueError("Cannot contain digits")
		return data

	def clean_password(self):
		data = self.cleaned_data['password']
		if len(data)<6:
			raise ValueError("Password Should Be Atleast 6 Characters")
		if len(data)>20:
			raise ValueError("Password Should Not Be More Than 20 Characters")	
		return data    

	def clean_mobile(self):
		data = self.cleaned_data['mobile']
		if len(data)!=10:
			raise ValueError("Mobile Number must be 10 digits")
		for k in data:
			if not k.isdigit():
				raise ValueError("Only Numbers Allowed in phone number")
			return data        
    
	def clean_email(self):
		data = self.cleaned_data['email']
		try:
			validate_email(data)
		except ValidationError:
			return ValueError("Enter a Valid Email ID")
		else:
			return data	
			
	def clean_gender(self):			  
		data = self.cleaned_data['gender']
		if(data not in ['M','F']):                    # Happens if HTML input form is overriden
			raise ValueError("Gender must be Male/Female")
		return data
    		

class AdminRegisterForm(forms.Form):
	"""Class based form to define fields for accepting Admin details
	to create a customer class and the corresponding record in the User class
	"""
    
	name = forms.CharField(max_length=20,  label="Full Name", required=True)
	emp_id = forms.CharField(max_length=10, label="Assigned Employee ID", required=True)
	email = forms.CharField(max_length=45, widget=forms.EmailInput, label="Email Address", required=True)
	password = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Password", required=True)
	repwd = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Confirm Password", required=True) 

	def clean_name(self):
		data = self.cleaned_data['name']
		for k in data:
			if k.isdigit():
				raise ValueError("Cannot contain digits")
		return data

	def clean_password(self):
		data = self.cleaned_data['password']
		if len(data)<6:
			raise ValueError("Password Should Be Atleast 6 Characters")
		if len(data)>20:
			raise ValueError("Password Should Not Be More Than 20 Characters")	
		return data  
	
	def clean_email(self):
		data = self.cleaned_data['email']
		try:
			validate_email(data)
		except ValidationError:
			return ValueError("Enter a Valid Email ID")
		else:
			return data	 
		
class PasswordChangeForm(forms.Form):
	""" Class based form to accept old password and new password, for allowing
	utililty to change password for users 
	"""

	oldpwd = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Current Password", required=True)
	password = forms.CharField(max_length=20, widget=forms.PasswordInput, label="New Password", required=True)
	repwd = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Confirm New Password", required=True)
	
	def clean_password(self):
		data = self.cleaned_data['password']
		if len(data)<6:
			raise ValueError("Password Should Be Atleast 6 Characters")
		if len(data)>20:
			raise ValueError("Password Should Not Be More Than 20 Characters")	
		return data   
			    

