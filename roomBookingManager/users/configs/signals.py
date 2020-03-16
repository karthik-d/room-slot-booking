""" Signals associated with the User-Domain of the Application to populate the database initially"""

from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User, Admin, EmployeeID
from users.constants import BASE_ADMIN, EMPLOYEE_PREFIXES

#To create groups (under post_migrate signal)
def create_groups(**kwargs):

	customerGroup,createdCustomer = Group.objects.get_or_create(name="CustomerPrivilege")
	managerGroup,createdManager = Group.objects.get_or_create(name="ManagerPrivilege")
	adminGroup,createdAdmin = Group.objects.get_or_create(name="AdminPrivilege")
	targetModel = ContentType.objects.get_for_model(User)
       
	view_admin_perm, created = Permission.objects.get_or_create(codename='can_view_admin', 
    											name='Can View Admin',
    											content_type=targetModel)
	if(created):
		adminGroup.permissions.add(view_admin_perm)
		managerGroup.permissions.add(view_admin_perm)
											
	view_employee_perm, created = Permission.objects.get_or_create(codename='can_view_employee', 
    												name='Can View Employee',
    												content_type=targetModel)
	if(created):
		adminGroup.permissions.add(view_employee_perm)
		customerGroup.permissions.add(view_employee_perm)
		managerGroup.permissions.add(view_employee_perm)
    													
	view_customer_perm, created = Permission.objects.get_or_create(codename='can_view_customer', 
    												name='Can View Customer',
    												content_type=targetModel)
	if(created):
		adminGroup.permissions.add(view_customer_perm)	
		managerGroup.permissions.add(view_customer_perm)	
		
def create_base_admin(**kwargs):
	""" A post migrate signal to create the base_admin if and when database is reset
	and ensure that base_admin always exists
	"""

	try:
		Admin.objects.get(emp_id__emp_id="ADM001")    # Checking if base admin exists
	except Admin.DoesNotExist:	
		admin_user = User.objects.create_user(
										email=BASE_ADMIN['email'],    #  Default for base_admin   
										is_staff=True,
										is_superuser=True,
										)
		admin_user.set_password(BASE_ADMIN['pwd'])			# Default initial password
		admin_user.name = BASE_ADMIN['name']
		admin_user.save()
		
		new_empid = EmployeeID()
		new_empid.emp_id = BASE_ADMIN['emp_id']
		new_empid.emp_type = 'admin'
		new_empid.creator = None                 # Remains as None for the base_admin
		new_empid.assignee = admin_user
		new_empid.save()
		
		admin = Admin()
		admin.instance = admin_user
		admin.emp_id = new_empid
		admin.save()
		
		adm_group = Group.objects.get(name="AdminPrivilege")
		adm_group.user_set.add(admin_user)				
				
