from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import UserHandler, UserDetail, CustomerHandler, ManagerHandler, AdminHandler, RoomHandler, SlotHandler, RoomDetail, SlotDetail, ManagerDetail, CustomerDetail, AdminDetail, AllReservations, PastReservations, FutureReservations, OngoingReservations, CancelledReservations, InactiveReservationDetail, ActiveReservationManage

urlpatterns = [
	path('user-handler/', UserHandler.as_view(), name='user-handler'),
	path('user-detail/<int:id>/', UserDetail.as_view(), name='user-detail'),	
    path('cust-handler/', CustomerHandler.as_view(), name='customer-handler'),
    path('cust-detail/<int:id>/', CustomerDetail.as_view(), name='customer-detail'),
    path('manager-handler/', ManagerHandler.as_view(), name='manager-handler'),
    path('manager-detail/<int:id>/', ManagerDetail.as_view(), name='manager-detail'),
    path('admin-handler/', AdminHandler.as_view(), name='admin-handler'),
    path('admin-detail/<int:id>/', AdminDetail.as_view(), name='admin-detail'),
    path('room-handler/', RoomHandler.as_view(), name='room-handler'),
    path('slot-handler/', SlotHandler.as_view(), name='slot-handler'),
    path('room-detail/<str:room_no>/', RoomDetail.as_view(), name='room-detail'),
    path('slot-detail/<int:id>/', SlotDetail.as_view(), name='slot-detail'),
    path('all-reserves/', AllReservations.as_view(), name='all-reserves'),
    path('past-reserves/', PastReservations.as_view(), name='past-reserves'),
    path('future-reserves/', FutureReservations.as_view(), name='future-reserves'),
    path('occupied-reserves/', OngoingReservations.as_view(), name='occupied-reserves'),
    path('cancelled-reserves/', CancelledReservations.as_view(), name='cancelled-reserves'),
    path('reserve-detail/<int:id>/', InactiveReservationDetail.as_view(), name='reserve-detail'),
    path('reserve-manage/<int:id>/', ActiveReservationManage.as_view(), name='reserve-manage'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
