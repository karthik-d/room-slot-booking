from django.urls import path
from .views import GenerateEmployeeID

urlpatterns = [
	path('generate-id', GenerateEmployeeID.as_view(), name="GenerateID"),
	]
