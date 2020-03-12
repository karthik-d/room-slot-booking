from django import forms

class CustomerRegisterForm(forms.Form):
    
	name = forms.CharField(max_length=20,label="Full Name",required=True)
	email = forms.EmailField(max_length=45,widget=forms.EmailInput,label="Email Address",required=True)
	password = forms.CharField(max_length=20,widget=forms.PasswordInput,label="Password",required=True)
	repwd = forms.CharField(max_length=20,widget=forms.PasswordInput,label="Confirm Password",required=True)    
	mobile = forms.CharField(max_length=10,label="Mobile Number",required=True)
	gender = forms.ChoiceField(choices=(("M","Male"),("F","Female")),label="Gender")

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
		return data    

	def clean_mobile(self):
		data = self.cleaned_data['mobile']
		if len(data)!=10:
			raise ValueError("Mobile Number must be 10 digits")
		for k in data:
			if not k.isdigit():
				raise ValueError("Only Numbers Allowed")
			return data
        
    # Email is validated by the EmailField class of django   
    
class ManagerRegisterForm(forms.Form):
    
	name = forms.CharField(max_length=20,  label="Full Name", required=True)
	emp_id = forms.CharField(max_length=10, label="Assigned Employee ID", required=True)
	email = forms.EmailField(max_length=45, widget=forms.EmailInput, label="Email Address", required=True)
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
		return data    

	def clean_mobile(self):
		data = self.cleaned_data['mobile']
		if len(data)!=10:
			raise ValueError("Mobile Number must be 10 digits")
		for k in data:
			if not k.isdigit():
				raise ValueError("Only Numbers Allowed")
			return data        
    # Email is validated by the EmailField class of django    
    

class AdminRegisterForm(forms.Form):
    
	name = forms.CharField(max_length=20,  label="Full Name", required=True)
	emp_id = forms.CharField(max_length=10, label="Assigned Employee ID", required=True)
	email = forms.EmailField(max_length=45, widget=forms.EmailInput, label="Email Address", required=True)
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
		return data   
		
class PasswordChangeForm(forms.Form):
	oldpwd = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Current Password", required=True)
	password = forms.CharField(max_length=20, widget=forms.PasswordInput, label="New Password", required=True)
	repwd = forms.CharField(max_length=20, widget=forms.PasswordInput, label="Confirm New Password", required=True)
	
	def clean_password(self):
		data = self.cleaned_data['password']
		if len(data)<6:
			raise ValueError("Password Should Be Atleast 6 Characters")
		return data 
			    
		
'''class InchargeRegistration(forms.Form):
    
    username = forms.CharField(max_length=10,label="Register Number",required=True)
    name = forms.CharField(max_length=20,label="Full Name",required=True)
    password = forms.CharField(max_length=20,widget=forms.PasswordInput,label="Password",required=True)
    repwd = forms.CharField(max_length=20,widget=forms.PasswordInput,label="Confirm Password",required=True)
    email = forms.EmailField(max_length=45,widget=forms.EmailInput,label="Email Address",required=True)
    mobile = forms.CharField(max_length=10,label="Mobile Number",required=True)
    club_name = forms.CharField(max_length=20,label="Club Name")
    gender = forms.ChoiceField(choices=(("M","Male"),("F","Female")),label="Gender",required=True)

    def clean_name(self):
        data = self.cleaned_data['name']
        for k in data:
            if k.isdigit():
                raise ValueError("Name Cannot contain digits")
        return data

    def clean_password(self):
        data = self.cleaned_data['password']
        if len(data)<5:
            raise ValueError("Password Should Be Atleast 5 Characters")
        return data    

    def clean_mobile(self):
        data = self.cleaned_data['mobile']
        if len(data)!=10:
            raise ValueError("Mobile Number must be 10 digits")
        for k in data:
            if not k.isdigit():
                raise ValueError("Only Numbers Allowed in Mobile Number")
        return data
        '''
