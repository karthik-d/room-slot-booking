from django.urls import path
from .views import CreateRoom, CreateSlot, ManageRooms, ManageSlots, DeleteRoom, DeleteSlot, ModifySlot, ViewReservations

urlpatterns = [
	path('add-room', CreateRoom.as_view(), name="RoomCreation"),
	path('add-slot', CreateSlot.as_view(), name="SlotCreation"),
	path('manage-rooms', ManageRooms.as_view(), name="ManageRooms"),
	path('manage-slots', ManageSlots.as_view(), name="ManageSlots"),
	path('delete-room', DeleteRoom.as_view(), name="DeleteRoom"),
	path('delete-slot', DeleteSlot.as_view(), name="DeleteSlot"),
	path('modify-slot', ModifySlot.as_view(), name="ModifySlot"),
	path('view-reserve', ViewReservations.as_view(), name="ViewReserve"),
]
