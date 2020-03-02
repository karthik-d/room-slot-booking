from django.contrib import admin
from .models import User, Customer, Manager, Admin, EmployeeID

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Manager)
admin.site.register(Admin)
admin.site.register(EmployeeID)

	
