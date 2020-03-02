from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from .forms import EmployeeIDGeneration
from users.models import Admin, EmployeeID
from users.constants import EMPLOYEE_PREFIXES


class GenerateEmployeeID(View):
	form = EmployeeIDGeneration()
	template = 'admin_iface/DisplayForm.html'
	
	def verify_password(self,request,pwd):
		user_email = request.user.email		
		if(authenticate(request,email=user_email,password=pwd)):
			return True
		else:
			return False	
	
	def post(self,request,*args,**kwargs):
		self.form = EmployeeIDGeneration(request.POST)
		
		try:
			if(self.form.is_valid()):
				if(self.verify_password(request,self.form.cleaned_data['password'])):
				
					emp_typ = self.form.cleaned_data['designation']
					pre = EMPLOYEE_PREFIXES[emp_typ]
					serial = pre+(str(EmployeeID.objects.filter(emp_type=emp_typ).count()+1).rjust(3,'0'))
					this_admin = Admin.objects.filter(instance__email=request.user.email)[0]
					
					new_empid = EmployeeID(emp_id=serial, emp_type=emp_typ, creator=this_admin)
					new_empid.save()
					
					messages.add_message(request, messages.SUCCESS, "Employee ID Generated - "+serial)
					'''SEND A MAIL '''
					return HttpResponseRedirect(reverse('GenerateID'))
					
				else:
					raise ValueError("Incorrect Password!\nAuthentication Failed")
					
			else:
				raise ValueError("Invalid Form")	
					
		except ValueError as prob:
			messages.add_message(request, messages.ERROR, prob)
			return HttpResponseRedirect(reverse('GenerateID'))	
				
		except KeyError:
			messages.add_message(request, message.ERROR, "Invalid Designation Entered")
			return HttpResponseRedirect(reverse('GenerateID'))		
				
	
	def get(self,request,*args,**kwargs):
		cont = dict()
		cont['form'] = self.form
		cont['prompt'] = "Create New Employee"
		return render(request, self.template, context=cont)
		
