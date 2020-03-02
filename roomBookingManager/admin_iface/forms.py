from django import forms    
from users.constants import EMPLOYEE_PREFIXES

class EmployeeIDGeneration(forms.Form):
	
	designation = forms.ChoiceField(choices=tuple(zip(EMPLOYEE_PREFIXES.keys(),map(str.title,EMPLOYEE_PREFIXES.keys()))),
									label="Designation",
									required=True)  
	# Only one designation available now
	password = forms.CharField(max_length=20,widget=forms.PasswordInput,label="Confirm Your Password",required=True)
	
	def clean_password(self):
		data = self.cleaned_data['password']
		return data
