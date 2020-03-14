from django.urls import path
from django.contrib.auth.views import LoginView  # Built-in view for Login
from .views import RegisterCustomer, RegisterManager, RegisterAdmin, Logout, ViewUserProfile, ChangePassword
from roomBookingManager.decorators import anonymous_required

urlpatterns = [
	path('customer-signup', RegisterCustomer.as_view(), name="CustomerRegistration"),
	path('manager-signup', RegisterManager.as_view(), name="ManagerRegistration"),
	path('admin-signup', RegisterAdmin.as_view(), name="AdminRegistration"),
	path('change-pwd', ChangePassword.as_view(), name="ChangePassword"),
	path('logout', Logout.as_view(), name="Logout"),
	path('login', anonymous_required()(LoginView.as_view(template_name="users/LogForm.html")), name="Login"),
	path('profile', ViewUserProfile.as_view(), name="ViewProfile"),
	path('profile/<int:user_id>', ViewUserProfile.as_view(), name="ViewProfileById"),
	]

				
