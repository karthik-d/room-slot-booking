from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from roomBookingManager.decorators import group_required, anonymous_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Customer, Manager, Admin, User, EmployeeID
from .forms import CustomerRegisterForm, ManagerRegisterForm, AdminRegisterForm, PasswordChangeForm

# @class_decorator(anonymous_required(redirect_url="/users/login"))
@method_decorator(anonymous_required('home'), name='dispatch')
class RegisterCustomer(View):
	""" Class based view to handle registation of a new Customer, collecting data 
	and updating the User and relevant databases
	"""

	form = CustomerRegisterForm()
	template = "users/DisplayForm.html"
	
	def email_exits(self,value):
		if(User.objects.filter(email=value).count()==0):
			return False
		else:
			return True
	
	def post(self,request,*args,**kwargs):
		try:
			self.form = CustomerRegisterForm(request.POST)
			if self.form.is_valid():    
		    # Check if all required fields are filed, else ValueError is raised                
				if(request.POST['repwd']!=request.POST['password']):
					raise ValueError("Passwords Must Match")
				if(self.email_exits(self.form.cleaned_data['email'])):
					raise ValueError("Email Already Exists. Please Login")
				
		        
				user = User.objects.create_user(
		        								email=self.form.cleaned_data['email'],
		        								is_staff=False,
		        								is_superuser=False,
		        								)
				user.set_password(request.POST['password'])
				user.name = self.form.cleaned_data['name']
				user.save()

				new_cust = Customer()
				new_cust.instance = user
				new_cust.phone = self.form.cleaned_data['mobile']
				new_cust.gender = self.form.cleaned_data['gender']
				new_cust.save()
		        
				cust_group = Group.objects.get(name="CustomerPrivilege")
				cust_group.user_set.add(user)

				messages.add_message(request, messages.SUCCESS, 'Customer Registered Successfully!')
				return HttpResponseRedirect(reverse('Login') )
			else:
				raise ValueError("Form is invalid")	
        
		except ValueError as prob:
			messages.add_message(request, messages.ERROR, prob)
			return HttpResponseRedirect(reverse('CustomerRegistration'))
		
	def get(self,request,*args,**kwargs):
		cont = dict()
		cont['form'] = self.form
		cont['prompt'] = "Customer Registration"
		return render(request, self.template, context=cont)


@method_decorator(anonymous_required('home'), name='dispatch')		
class RegisterManager(View):
	""" Class based view to handle registation of a new Manager, collecting data 
	and updating the User and relevant databases
	"""
	
	form = ManagerRegisterForm()
	template = "users/DisplayForm.html"
	
	def email_exits(self,value):
		if(User.objects.filter(email=value).count()==0):
			return False
		else:
			return True	
			
	def id_exits(self,value):
		if(Manager.objects.filter(emp_id=value).count()==0):
			return False
		else:
			return True	
			
	def id_valid(self,value):
		existing_ids = tuple(map(str,EmployeeID.objects.all()))
		if(value in existing_ids):
			if(value[:3]=="MAN"):   # Must be manager type employee ID
				return True
			else:
				return False	
		else:
			return False	
		# It is not necessary to check if the assignee is None
		# If it was already assigned, id_exists would've returned True 
		# and the process would already be terminated						
	
	def post(self,request,*args,**kwargs):
		try:
			self.form = ManagerRegisterForm(request.POST)
			if self.form.is_valid():    
		    # Check if all required fields are filed, else ValueError is raised                
				if(request.POST['repwd']!=request.POST['password']):
					raise ValueError("Passwords Must Match")
				if(self.email_exits(self.form.cleaned_data['email'])):
					raise ValueError("Email Already Exists. Please Login")
				if(self.id_exits(self.form.cleaned_data['emp_id'])):
					raise ValueError("Enter Your Assigned Employee ID. Contact Admin for more details")	
				if(not self.id_valid(self.form.cleaned_data['emp_id'])):
					raise ValueError("Invalid Employee ID. Contact Admin for more details")						
		        
				user = User.objects.create_user(
		        								email=self.form.cleaned_data['email'],
		        								is_staff=True,
		        								is_superuser=False,
		        								)
				user.set_password(request.POST['password'])
				user.name = self.form.cleaned_data['name']
				user.save()
				
				mod_empid = EmployeeID.objects.filter(emp_id=self.form.cleaned_data['emp_id'])[0]
				mod_empid.assignee = user
				mod_empid.save()				

				new_man = Manager()
				new_man.instance = user
				new_man.emp_id = mod_empid
				new_man.phone = self.form.cleaned_data['mobile']
				new_man.gender = self.form.cleaned_data['gender']
				new_man.save()
		        
				man_group = Group.objects.get(name="ManagerPrivilege")
				man_group.user_set.add(user)

				messages.add_message(request, messages.SUCCESS, 'Manager Registered Successfully!')
				return HttpResponseRedirect(reverse('Login') )
			else:
				raise ValueError("Form is invalid")	
        
		except ValueError as prob:
			messages.add_message(request, messages.ERROR, prob)
			return HttpResponseRedirect(reverse('ManagerRegistration') )
		
	def get(self,request,*args,**kwargs):
		cont = dict()
		cont['form'] = self.form
		cont['prompt'] = "Manager Registration"
		return render(request, self.template, context=cont)	
		

@method_decorator(anonymous_required('home'), name='dispatch')		
class RegisterAdmin(View):
	""" Class based view to handle registation of a new Admin, collecting data 
	and updating the User and relevant databases
	"""
	
	form = AdminRegisterForm()
	template = "users/DisplayForm.html"
	
	def email_exits(self,value):
		if(User.objects.filter(email=value).count()==0):
			return False
		else:
			return True	
			
	def id_exits(self,value):  # Return True if id exists in Admin database
		if(Admin.objects.filter(emp_id=value).count()==0):
			return False
		else:
			return True	
			
	def id_valid(self,value):
		existing_ids = tuple(map(str,EmployeeID.objects.all()))
		if(value in existing_ids):
			if(value[:3]=="ADM"):   # Must be admin type employee ID
				if(value!="ADM001"):  # Must not be base_admin
					return True
				else:
					return False	
			else:
				return False	
		else:
			return False	
		# It is not necessary to check if the assignee is None
		# If it was already assigned, id_exists would've returned True 
		# and the process would already be terminated						
	
	def post(self,request,*args,**kwargs):
		try:
			self.form = AdminRegisterForm(request.POST)
			if self.form.is_valid():    
		    # Check if all required fields are filed, else ValueError is raised                
				if(request.POST['repwd']!=request.POST['password']):
					raise ValueError("Passwords Must Match")
				if(self.email_exits(self.form.cleaned_data['email'])):
					raise ValueError("Email Already Exists. Please Login")
				if(self.id_exits(self.form.cleaned_data['emp_id'])):
					raise ValueError("Enter Your Assigned Employee ID. Contact Admin for more details")	
				if(not self.id_valid(self.form.cleaned_data['emp_id'])):
					raise ValueError("Invalid Employee ID. Contact Admin for more details")						
		        
				user = User.objects.create_user(
		        								email=self.form.cleaned_data['email'],
		        								is_staff=True,
		        								is_superuser=True
		        								)
				user.set_password(request.POST['password'])
				user.name = self.form.cleaned_data['name']
				user.save()
				
				mod_empid = EmployeeID.objects.get(emp_id=self.form.cleaned_data['emp_id'])
				mod_empid.assignee = user
				mod_empid.save()				

				new_adm = Admin()
				new_adm.instance = user
				new_adm.emp_id = mod_empid
				new_adm.save()
		        
				adm_group = Group.objects.get(name="AdminPrivilege")
				adm_group.user_set.add(user)

				messages.add_message(request, messages.SUCCESS, 'Admin Registered Successfully!')
				return HttpResponseRedirect(reverse('Login') )
			else:
				raise ValueError("Form is invalid")	
        
		except ValueError as prob:
			messages.add_message(request, messages.ERROR, prob)
			return HttpResponseRedirect(reverse('AdminRegistration') )
		
	def get(self,request,*args,**kwargs):
		cont = dict()
		cont['form'] = self.form
		cont['prompt'] = "Admin Registration"
		return render(request, self.template, context=cont)		


@method_decorator(login_required, name="dispatch")		
class ChangePassword(View):
	"""Class based View to change a user's password using his old password
	"""
	
	form = PasswordChangeForm()	
	template = "users/DisplayForm.html"
	
	def post(self, request):
		try:
			self.form = PasswordChangeForm(request.POST)
			if self.form.is_valid():    
		    # Check if all required fields are filled, else ValueError is raised                
				if(self.form.cleaned_data['repwd']!=self.form.cleaned_data['password']):
					raise ValueError("New Passwords Must Match")
			else:
				raise ValueError("Form is invalid")	
			
			this_user = request.user
			old_pwd = self.form.cleaned_data['oldpwd']
			cnf_user = authenticate(email=this_user.email, password=old_pwd)
			if(cnf_user):
				cnf_user.set_password(self.form.cleaned_data['password'])
				cnf_user.save()
			else:
				raise ValueError("Password Incorrect!")	
				
			messages.add_message(request, messages.SUCCESS, "Password Reset. Logging Out...")
			return HttpResponseRedirect(reverse('Logout'))	
        
		except ValueError as prob:
			messages.add_message(request, messages.ERROR, prob)
			return HttpResponseRedirect(reverse('home') )		
		
	
	def get(self, request):
		cont = dict()
		cont['form'] = self.form
		cont['prompt'] = "Change Password"
		return render(request, self.template, context=cont)
		

@method_decorator(login_required, name='dispatch')
class ViewUserProfile(View):
	"""Class based View to view a users profile, after ensuring that 
	the requesting user has permission to do so
	"""
	
	template = "users/Profile.html"
	resolve_gender = {"M":"Male","F":"Female"}
	
	def post(self,request,*args,**kwargs):
		""" Post method works based on the user's email ID
		"""
		
		email = list(request.POST.keys())[1]
		if(email=="csrfmiddlewaretoken"):
			email = list(request.POST.keys())[0]
		try:
		    targetUser = list(User.objects.filter(email=email))[0]        # User to be displayed
		except IndexError:
		    messages.add_message(request, messages.ERROR, "User Could Not Be Found!")
		    return HttpResponseRedirect(reverse('home'))
		    
		targetGroup=list(Group.objects.filter(user=targetUser))[0].name   # Group of user to be displayed	
		
		try:
			if(targetGroup=="CustomerPrivilege"):
				if(request.user.has_perm('users.can_view_customer')):				
					targetSpecific = list(Customer.objects.filter(instance=targetUser))[0]  # Customer instance
					typ = "Customer"
					gender = self.resolve_gender[targetSpecific.gender]
					person_id = "Not Applicable"
				else:
					raise ValueError('Permission Denied')
					
			elif(targetGroup=="ManagerPrivilege"):
				if(request.user.has_perm('users.can_view_employee')):	
					targetSpecific = list(Manager.objects.filter(instance=targetUser))[0]  # Manager Instance
					typ = "Manager"
					gender = targetSpecific.gender
					person_id = targetSpecific.emp_id
				else:
					raise ValueError('Permission Denied')
				
			elif(targetGroup=="AdminPrivilege"):
				if(request.user.has_perm('users.can_view_admin')):			
					targetSpecific = list(Admin.objects.filter(instance=targetUser))[0]  # Admin Instance
					typ = "Admin"    
					gender = "Not Specified"
					person_id = targetSpecific.admin_id
				else:
					raise ValueError('Permission Denied')
			
			cont = {"Name":targetUser.name,
		        	"Email":targetUser.email,
		        	"Gender":gender,
		        	"Type":typ,
		        	"ID":person_id,
		        	"UserID":targetUser.id}	
		        		
		except ValueError as prob:
				val = request.user.get_all_permissions()
				messages.add_message(request, messages.SUCCESS, 'Permission Denied') 
				return HttpResponseRedirect(reverse('home'))     
		return render(request,self.template,context=cont)
	
	def get(self, request, user_id, *args, **kwargs):
		""" Get method works based on the user's id - assigned automatically during user
		creation by django models
		"""
		
		try:
		    targetUser = list(User.objects.filter(id=user_id))[0]        # User to be displayed
		except IndexError:
		    messages.add_message(request, messages.ERROR, "User Could Not Be Found!")
		    return HttpResponseRedirect(reverse('home'))
		    
		targetGroup=list(Group.objects.filter(user=targetUser))[0].name   # Group of user to be displayed	
		
		try:
			if(targetGroup=="CustomerPrivilege"):
				if(request.user.has_perm('users.can_view_customer')):				
					targetSpecific = list(Customer.objects.filter(instance=targetUser))[0]  # Customer instance
					typ = "Customer"
					gender = self.resolve_gender[targetSpecific.gender]
					person_id = "Not Applicable"
				else:
					raise ValueError('Permission Denied')
					
			elif(targetGroup=="ManagerPrivilege"):
				if(request.user.has_perm('users.can_view_employee')):	
					targetSpecific = list(Manager.objects.filter(instance=targetUser))[0]  # Manager Instance
					typ = "Manager"
					gender = targetSpecific.gender
					person_id = targetSpecific.emp_id
				else:
					raise ValueError('Permission Denied')
				
			elif(targetGroup=="AdminPrivilege"):
				if(request.user.has_perm('users.can_view_admin')):			
					targetSpecific = list(Admin.objects.filter(instance=targetUser))[0]  # Admin Instance
					typ = "Admin"    
					gender = "Not Specified"
					person_id = targetSpecific.emp_id.emp_id
				else:
					raise ValueError('Permission Denied')
			
			cont = {"Name":targetUser.name,
		        	"Email":targetUser.email,
		        	"Gender":gender,
		        	"Type":typ,
		        	"ID":person_id,
		        	"UserID":targetUser.id}	
		        		
		except ValueError as prob:
				val = request.user.get_all_permissions()
				messages.add_message(request, messages.SUCCESS, 'Permission Denied') 
				return HttpResponseRedirect(reverse('home'))     

		return render(request,self.template,context=cont)


# @class_decorator(login_required(login_url='/users/login',redirect_field_name="/"))
@method_decorator(login_required, name='dispatch')
class Logout(View):
	"""Class based View for performing logout operation for a user, redirecting to main page
	"""

	def get(self,request,*args,**kwargs):
		logout(request)
		messages.add_message(request, messages.SUCCESS, 'Logged Out!')
		return HttpResponseRedirect(reverse('home') )	
		
		
	
			
'''
def register_student(request):
    cont = dict()
    if request.method == 'POST':
        form = StudentRegistration(request.POST)
        try:
            if form.is_valid():    # Check if all required fields are filed
                if(request.POST['repwd']!=request.POST['password']):
                    raise ValueError("Passwords Must Match")
                
                user = User.objects.create_user(username=form.cleaned_data['username'],
                                 email=form.cleaned_data['email'])
                user.set_password(request.POST['password'])
                user.p_name = form.cleaned_data['name']
                user.save()

                newCust = Student()
                newCust.reg_num = user
                newCust.name = form.cleaned_data['name']
                newCust.email = form.cleaned_data['email']
                newCust.phone = form.cleaned_data['mobile']
                newCust.year = form.cleaned_data['year']
                newCust.section = form.cleaned_data['section']
                newCust.gender = form.cleaned_data['gender']
                newCust.save()
                
                studGroup = Group.objects.get(name="studentPrivilege")
                studGroup.user_set.add(user)

                messages.add_message(request, messages.SUCCESS, 'Student Registered Successfully!')
                return HttpResponseRedirect(reverse('mainLanding') )
            
        except ValueError as prob:
            messages.add_message(request, messages.ERROR, prob)
    else:
        form = StudentRegistration()

    cont['form'] = form
    cont['prompt'] = "SignUp as Student"
    return render(request, 'users/displayForm.html', context=cont)'''
    
