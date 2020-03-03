from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User

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
	
	# Admins are allowed to view the public profile information of other admins, customers and employees		
	# Managers are allowed to view the public profile information of customers only
	# Customers can view their own and manager(i.e.employee) profiles
