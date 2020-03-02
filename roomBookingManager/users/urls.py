from django.urls import path
from django.contrib.auth.views import LoginView  # Built-in view for Login
from .views import RegisterCustomer, RegisterManager, Logout, ViewUserProfile

urlpatterns = [
	path('customer-signup', RegisterCustomer.as_view(), name="CustomerRegistration"),
	path('manager-signup', RegisterManager.as_view(), name="ManagerRegistration"),
	path('logout', Logout.as_view(), name="Logout"),
	path('login', LoginView.as_view(template_name="users/LogForm.html"), name="Login"),
	path('profile', ViewUserProfile.as_view(), name="ViewProfile"),
	]

				
