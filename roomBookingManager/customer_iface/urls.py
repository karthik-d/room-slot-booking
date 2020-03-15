from django.urls import path
from .views import FindSlot, ReserveSlot, ManageReservations, DeleteReservation

urlpatterns = [
	path('find-slot', FindSlot.as_view(), name='FindSlot'),
	path('reserve-slot', ReserveSlot.as_view(), name='ReserveSlot'),
	path('manage-reserve', ManageReservations.as_view(), name='ManageReserve'),
	path('delete-reserve', DeleteReservation.as_view(), name='DeleteReserve'),
]
