from django import forms
from datetime import datetime

'''def __init__(self,dynData,*args,**kwargs):
		super.__init__(*args,**kwargs) '''

class SlotFindForm(forms.Form):
	""" Form class to accept date input for room reservation from customer
	"""	
	
	def __init__(self,*args,**kwargs):
		super(SlotFindForm,self).__init__(*args,**kwargs)
		date_now = datetime.date(datetime.now())
		self.fields['date'].widget=forms.TextInput(attrs={'type':'date','min':date_now})
	
	date = forms.DateField(required=True,label="Date",widget=forms.TextInput(attrs={'type': 'date'}))
	
	def clean_date(self):
		data = self.cleaned_data['date']
		if(data<datetime.date(datetime.now())):
			raise ValueError("Date Must Be In Future")
		
	
