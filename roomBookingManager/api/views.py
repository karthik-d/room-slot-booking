from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, CustomerSerializer, ManagerSerializer, RoomSerializer, SlotSerializer, ReservationLinkSerializer, ReservationSerializer, ActiveReservationSerializer
from users.models import User, Customer, Manager
from manager_iface.models import Room, Slot
from customer_iface.models import IsolatedResData, Reservation
from datetime import datetime

class UserHandler(APIView):    # For a list of users
	"""
	List all snippets, or create a new snippet.
	"""
    
	def get(self, request, format=None):
		users = User.objects.all()
		serializer = UserSerializer(users, many=True, context={'request':request})    # Since there can be multiple users
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = UserSerializer(data=request.data, context={'request':request})     # .data alternative to POST, 
		if serializer.is_valid():						      # can handle arbitrary data
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(generics.RetrieveAPIView):     # Read-Only for an individual user
	queryset = User.objects.all()
	serializer_class = UserSerializer    
	lookup_field = 'id'  
	
	def delete(self, request, id):
		try:
			user = User.objects.get(id=id)
		except User.DoesNotExist:
			return Response({"message": "User not found."}, status=404)	
		else:	
			user.delete()
			return Response({"message": "User and relevant data have been deleted."}, status=204)		
    
    
class CustomerHandler(APIView):    # For a list of users
	"""
    List all snippets, or create a new snippet.
	"""
	def get(self, request, format=None):
		users = Customer.objects.all()
		serializer = CustomerSerializer(users, many=True, context={'request':request})    # Since there can be multiple users
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = CustomerSerializer(data=request.data, context={'request':request})     # .data alternative to POST, 
		if serializer.is_valid():						      # can handle arbitrary data
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CustomerDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual customer
	queryset = Customer.objects.all()
	serializer_class = CustomerSerializer  
	custom_lookup_field = 'id' 
    
	def get_object(self):     # OVERRIDING the get_object method to pdefine customised object lookup
		queryset = User.objects.all()
		filter = dict()
		field = self.custom_lookup_field
		filter[field] = self.kwargs[field]
		user = get_object_or_404(queryset, **filter)
		self.check_object_permissions(self.request, user)
		return user.customer 
		
	def delete(self, request, id):
		try:
			user = User.objects.get(id=id)
		except User.DoesNotExist:
			return Response({"message": "Customer not found."}, status=404)	
		else:	
			user.delete()
			return Response({"message": "Customer and relevant data have been deleted."}, status=204)	
			  
        
class ManagerHandler(APIView):    # For a list of users
	"""
    List all snippets, or create a new snippet.
    """
	def get(self, request, format=None):
		users = Manager.objects.all()
		serializer = ManagerSerializer(users, many=True, context={'request':request})    # Since there can be multiple users
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = ManagerSerializer(data=request.data, context={'request':request})     # .data alternative to POST, 
		if serializer.is_valid():						      # can handle arbitrary data
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
	        
class ManagerDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual manager
	queryset = Manager.objects.all()
	serializer_class = ManagerSerializer  
	custom_lookup_field = 'id'
    
	def get_object(self):     # OVERRIDING the get_object method to pdefine customised object lookup
		queryset = User.objects.all()
		filter = dict()
		field = self.custom_lookup_field
		filter[field] = self.kwargs[field]
		user = get_object_or_404(queryset, **filter)
		self.check_object_permissions(self.request, user)
		return user.manager
		
	def delete(self, request, id):
		try:
			user = User.objects.get(id=id)
		except User.DoesNotExist:
			return Response({"message": "Manager not found."}, status=404)	
		else:	
			user.delete()
			return Response({"message": "Manager and relevant data have been deleted."}, status=204)				
    
class RoomHandler(generics.RetrieveAPIView):
	"""
	"""
	queryset = Room.objects.all()
	
	def get(self, request, format=None):
		rooms = Room.objects.all()
		serializer = RoomSerializer(rooms, many=True, context={'request':request})
		return Response(serializer.data)
		
class RoomDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual user
	queryset = Room.objects.all()
	serializer_class = RoomSerializer    
	lookup_field = 'room_no'  
	
	def delete(self, request, room_no):     # Overriding the default delete method 
		this_room = self.queryset.get(room_no=room_no)	
		# Simoultaneously setting status as Cancelled in Isolated Reservation Data
		# This is done using a pre_delete signal attached to Reservation model
		this_room.delete()
		return Response({"message": "Room and relevant data have been deleted."}, status=204)			
		
    
class SlotHandler(generics.RetrieveAPIView):
	"""
	"""
	queryset = Slot.objects.all()
	
	def get(self, request, format=None):
		slots = Slot.objects.all()
		serializer = SlotSerializer(slots, many=True, context={'request':request})
		return Response(serializer.data)	
		
class SlotDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual user
	queryset = Slot.objects.all()
	serializer_class = SlotSerializer    
	lookup_field = 'id'  
	
	def delete(self, request, id):     # Overriding the default delete method 
		this_slot = self.queryset.get(id=id)	
		# Simoultaneously setting status as Cancelled in Isolated Reservation Data
		# This is done using a pre_delete signal attached to Reservation model
		this_slot.delete()
		return Response({"message": "Slot and relevant data have been deleted."}, status=204)		
		
class AllReservations(APIView):    # For a list of users
	"""
    List all snippets, or create a new snippet.
    """
	def get(self, request, format=None):
		reserves = User.objects.filter(email=request.user.email)      # Dummy QuerySet with on Entry
		serializer = ReservationLinkSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data) 
        
class PastReservations(APIView):    # For a list of users
	"""
    List all snippets, or create a new snippet.
    """
	def get(self, request, format=None):
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())
		reserves = IsolatedResData.objects.filter(	date__lt=today,
        											status="Active")|(	                                                 			           IsolatedResData.objects.filter(	date=today,
        											end_time__lt=now,
        											status="Active"))
		serializer = ReservationSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data)   
        
class FutureReservations(APIView):    # For a list of users
	"""
    List all snippets, or create a new snippet.
    """
	def get(self, request, format=None):
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())
		reserves = Reservation.objects.filter(	date__gt=today)|(	                                                 			           Reservation.objects.filter(	date=today,
        										slot__start_time__gt=now))  # All reservations in this model are "Active"
		serializer = ActiveReservationSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data)               

class OngoingReservations(APIView):    # For a list of users
	"""
    List all snippets, or create a new snippet.
    """
	def get(self, request, format=None):
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())
		reserves = IsolatedResData.objects.filter(	date=today,
        											start_time__lte=now,
        											status="Active")|(	                                                 			           IsolatedResData.objects.filter(	date=today,
        											end_time__gte=now,
        											status="Active"))
		serializer = ReservationSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data)   
		
class CancelledReservations(APIView):    # For a list of users
	"""
    List all snippets, or create a new snippet.
    """
	def get(self, request, format=None):
		reserves = IsolatedResData.objects.filter(status='Cancelled')
		serializer = ReservationSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data)  		
		
class InactiveReservationDetail(generics.RetrieveAPIView):     # Read-Only for an individual user
	queryset = IsolatedResData.objects.all()
	serializer_class = ReservationSerializer    
	lookup_field = 'id'   
    
class ActiveReservationManage(generics.RetrieveDestroyAPIView):
	queryset = Reservation.objects.all()
	serializer_class = ActiveReservationSerializer    
	lookup_field = 'id'  
	
	def delete(self, request, id):     # Overriding the default delete method 
		this_reserve = self.queryset.get(id=id)	
		# Simoultaneously setting status as Cancelled in Isolated Reservation Data
		# This is done using a pre_delete signal attached to Reservation model
		this_reserve.delete()
		return Response({"message": "Reservation has been deleted."}, status=204)	
	          	
		                  

    
    
     
