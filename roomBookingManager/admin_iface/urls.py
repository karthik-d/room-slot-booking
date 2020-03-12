from django.urls import path
from .views import GenerateEmployeeID, ManageEmployeeID

urlpatterns = [
	path('generate-id', GenerateEmployeeID.as_view(), name="GenerateID"),
	path('manage-ids', ManageEmployeeID.as_view(), name="ManageID"),
	]
