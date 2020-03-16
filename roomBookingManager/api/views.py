""" Module to implement Views for all API Queries"""

from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from .serializers import UserSerializer, CustomerSerializer, ManagerSerializer, AdminSerializer, RoomSerializer, SlotSerializer, ReservationLinkSerializer, ReservationSerializer, ActiveReservationSerializer, EmployeeIDSerializer
from users.models import User, Customer, Manager, Admin, EmployeeID
from users.constants import EMPLOYEE_PREFIXES
from manager_iface.models import Room, Slot
from customer_iface.utilities import send_generated_key
from customer_iface.models import IsolatedResData, Reservation
from datetime import datetime


class GenerateAuthToken(APIView):
	""" Class based view to display how to create an API Authentication Token by GET request
	and Generate a token if user is admin by POST request
	"""

	def get(self, request):
		ret = dict()
		ret['message'] = "Obtain or view your API Authentication Token if you are an admin by sending a POST request to this URL"
		ret['format'] = "Required JSON format - {'email':<your_email_id>, 'password':<your_password>}"
		ret['example'] = "{'email':'admin@gmail.com', 'password':'secret'}"
		return Response(ret, status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		email = request.data['email']
		password = request.data['password']
    	# Getting User
		try:
			this_user = User.objects.get(email=email)
		except User.DoesNotExist:
			return Response({'error':"User Not Found"}, status=status.HTTP_404_NOT_FOUND)
    	# Verifying Password		
		cnf_user = authenticate(email=this_user.email, password=password)
		if(cnf_user):
			pass
		else:
			return Response({'error':"Authentication Failed"}, status=status.HTTP_401_UNAUTHORIZED)
    	# Checking if admin
		if(Group.objects.get(user=this_user).name=="AdminPrivilege"):
			pass
		else:	
			return Response({'error':"Must be admin"}, status=status.HTTP_401_UNAUTHORIZED)
    	# Generate and return authentication token		
		token, created = Token.objects.get_or_create(user=this_user)
		return Response({
            'token': token.key,
            'email': this_user.email
        }, status=status.HTTP_200_OK)


class UserHandler(APIView):    # For a list of users
	""" Class based API View to handle listing of users
	"""
	
	serializer_class = UserSerializer
	queryset = User.objects.all()
    
	def get(self, request, format=None):
		users = User.objects.all()
		serializer = UserSerializer(users, many=True, context={'request':request})    # Since there can be multiple users
		return Response(serializer.data)
		
	# CANNOT CREATE USER DIRECTLY, HAS TO BE CUSTOMER, MANAGER or ADMIN	


class UserDetail(generics.RetrieveAPIView):     # Read-Only for an individual user
	""" Class based API View to display and delete specific User instance
	details thrugh GET and DELETE requests
	"""
	
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
	""" Class based API View to handle listing and creation of Customers 
	through GET and POST reqquests
	"""
	
	serializer_class = CustomerSerializer
	queryset = Customer.objects.all()
	
	def get(self, request, format=None):
		users = Customer.objects.all()
		serializer = CustomerSerializer(users, many=True, context={'request':request})    # Since there can be multiple users
		return Response(serializer.data)

	def post(self, request, format=None):
		user_data = dict()
		user_data['email'] = request.data.pop('email')
		user_data['name'] = request.data.pop('name')
		user_data['password'] = request.data.pop('password', None)   # Password Required is tested here
		if(not user_data['password']):
			return Response({"error":"Password is required"}, status=status.HTTP_400_BAD_REQUEST)
		user_serial = (UserHandler().serializer_class)(data=user_data, context={'request':request})
		if(user_serial.is_valid()):
			serializer = (self.serializer_class)(data=request.data, context={'request':request})
			if(serializer.is_valid()):
				user_serial.save(is_staff=False, is_superuser=False)   # Saving if both serializers are valid
				user = User.objects.get(email=user_data['email'])
				serializer.save(instance=user)				
				cust_group = Group.objects.get(name="CustomerPrivilege")   # Adding to Customer Group
				cust_group.user_set.add(user)
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			else:
				err = serializer.errors	
		else:
			err = user_serial.errors			
		return Response(err, status=status.HTTP_400_BAD_REQUEST)
        
        
class CustomerDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual customer
	""" Class based API View to display and delete specific Customer user
	details thrugh GET and DELETE requests
	"""
	
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
	""" Class based API View to handle listing and creation of Managers 
	through GET and POST requests
	"""
	
	serializer_class = ManagerSerializer
	queryset = Manager.objects.all()
	
	def id_exists(self,value):  # TO VERIFY IF EMP_ID IS ALREADY ASSIGNED TO SOMEONE
		if(Manager.objects.filter(emp_id=value).count()==0):
			return False
		else:
			return True	
			
	def id_valid(self,value):   # TO VERIFY ID EMP_ID IS VALID
		existing_ids = tuple(map(str,EmployeeID.objects.all()))
		if(value in existing_ids):
			if(value[:3]=="MAN"):   # Must be manager type employee ID
				return True
			else:
				return False	
		else:
			return False	
    
	def get(self, request, format=None):
		users = Manager.objects.all()
		serializer = ManagerSerializer(users, many=True, context={'request':request})    # Since there can be multiple users
		return Response(serializer.data)

	def post(self, request, format=None):
		user_data = dict()
		user_data['email'] = request.data.pop('email')
		user_data['name'] = request.data.pop('name')
		user_data['password'] = request.data.pop('password', None)   # Password Required is tested here
		
		if(not user_data['password']):        # PASSWORD AND EMP_ID CHECKED HERE
			return Response({"error":"Password is required"}, status=status.HTTP_400_BAD_REQUEST)
		id_check = request.data.pop('emp_id', None)
		if(not id_check):	
			return Response({"error":"Employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)
		if((self.id_exists(id_check)) or (not self.id_valid(id_check))):
			return Response({"error":"Employee ID is invalid"}, status=status.HTTP_400_BAD_REQUEST)	
		empid_inst = EmployeeID.objects.get(emp_id=id_check)   # GETTING EMPLOYEE_ID RECORD OBJECT
			
		user_serial = (UserHandler().serializer_class)(data=user_data, context={'request':request})
		if(user_serial.is_valid()):
			serializer = (self.serializer_class)(data=request.data, context={'request':request})
			if(serializer.is_valid()):
				user_serial.save(is_staff=True, is_superuser=False)
				user = User.objects.get(email=user_data['email'])  # Saving after both serializers are valid
				empid_inst.assignee = user      
				empid_inst.save()				                   # Setting assignee for employee id instance        
				serializer.save(instance=user, emp_id=empid_inst)			# Saving User and Employee ID instances	
				manager_group = Group.objects.get(name="ManagerPrivilege")   # Adding to Manager Group
				manager_group.user_set.add(user)
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			else:
				err = serializer.errors	
		else:
			err = user_serial.errors			
		return Response(err, status=status.HTTP_400_BAD_REQUEST)
	        
	        
class ManagerDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual manager
	""" Class based API View to display and delete specific Manager user
	details through GET and DELETE requests
	"""
	
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
			
			
class AdminHandler(APIView):    # For a list of users
	""" Class based API View to handle listing and creation of Admins
	through GET and POST reqquests
	"""
	
	serializer_class = AdminSerializer
	queryset = Admin.objects.all()
    
	def id_exists(self,value):  # TO VERIFY IF EMP_ID IS ALREADY ASSIGNED TO SOMEONE
		if(Manager.objects.filter(emp_id=value).count()==0):
			return False
		else:
			return True	
			
	def id_valid(self,value):   # TO VERIFY ID EMP_ID IS VALID
		existing_ids = tuple(map(str,EmployeeID.objects.all()))
		if(value in existing_ids):
			if(value[:3]=="ADM"):   # Must be manager type employee ID
				return True
			else:
				return False	
		else:
			return False	
			
	def get(self, request, format=None):
		users = Admin.objects.all()
		serializer = AdminSerializer(users, many=True, context={'request':request})    # Since there can be multiple users
		return Response(serializer.data)

	def post(self, request, format=None):
		user_data = dict()
		user_data['email'] = request.data.pop('email')
		user_data['name'] = request.data.pop('name')
		user_data['password'] = request.data.pop('password', None)   # Password Required is tested here
		
		if(not user_data['password']):        # PASSWORD AND EMP_ID CHECKED HERE
			return Response({"error":"Password is required"}, status=status.HTTP_400_BAD_REQUEST)
		id_check = request.data.pop('emp_id', None)
		if(not id_check):	
			return Response({"error":"Employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)
		if((self.id_exists(id_check)) or (not self.id_valid(id_check))):
			return Response({"error":"Employee ID is invalid"}, status=status.HTTP_400_BAD_REQUEST)	
		empid_inst = EmployeeID.objects.get(emp_id=id_check)   # GETTING EMPLOYEE_ID RECORD OBJECT
			
		user_serial = (UserHandler().serializer_class)(data=user_data, context={'request':request})
		if(user_serial.is_valid()):
			serializer = (self.serializer_class)(data=request.data, context={'request':request})
			if(serializer.is_valid()):
				user_serial.save(is_staff=True, is_superuser=True)
				user = User.objects.get(email=user_data['email'])  # Saving after both serializers are valid
				empid_inst.assignee = user      
				empid_inst.save()				                   # Setting assignee for employee id instance        
				serializer.save(instance=user, emp_id=empid_inst)			# Saving User and Employee ID instances	
				adm_group = Group.objects.get(name="AdminPrivilege")   # Adding to Admin Group
				adm_group.user_set.add(user)
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			else:
				err = serializer.errors	
		else:
			err = user_serial.errors			
		return Response(err, status=status.HTTP_400_BAD_REQUEST)
        
	        
class AdminDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual manager
	""" Class based API View to display and delete specific Admin user
	details thrugh GET and DELETE requests
	"""
	
	queryset = Admin.objects.all()
	serializer_class = AdminSerializer  
	custom_lookup_field = 'id'
    
	def get_object(self):     # OVERRIDING the get_object method to pdefine customised object lookup
		queryset = User.objects.all()
		filter = dict()
		field = self.custom_lookup_field
		filter[field] = self.kwargs[field]
		user = get_object_or_404(queryset, **filter)
		self.check_object_permissions(self.request, user)
		return user.admin
		
	def delete(self, request, id):
		try:
			user = User.objects.get(id=id)
		except User.DoesNotExist:
			return Response({"message": "Admin not found."}, status=404)	
		else:	
			user.delete()
			return Response({"message": "Admin and relevant data have been deleted."}, status=204)


class EmpidHandler(APIView):    # For a list of users
	""" Class based API View to handle listing and creation of Employee IDs
	through GET and POST reqquests
	"""
	
	serializer_class = EmployeeIDSerializer
	queryset = EmployeeID.objects.all()
			
	def get(self, request, format=None):
		ids = EmployeeID.objects.all()
		serializer = EmployeeIDSerializer(ids, many=True, context={'request':request})   # Since there can be multiple users
		return Response(serializer.data)

	def post(self, request, format=None):
		emp_type = request.data['emp_type']		 
		creator = request.user    # Will be an Admin User only (Permission Controlled)				
		serializer = (self.serializer_class)(data=request.data, context={'request':request})
		if(serializer.is_valid()):  			                   # Setting assignee for employee id instance  
			pre = EMPLOYEE_PREFIXES[emp_type]          #GENERATING EMPLOYEE ID
			gen_empid = pre+(str(EmployeeID.objects.filter(emp_type=emp_type).count()+1).rjust(3,'0')) 
			      
			serializer.save(emp_id=gen_empid, creator=creator)
			empid_inst = EmployeeID.objects.get(emp_id=gen_empid)
			send_generated_key(empid_inst)    # SEND AN EMAIL to ADMIN
			return Response(serializer.data, status=status.HTTP_201_CREATED)			
		else:
			err = user_serial.errors			
		return Response(err, status=status.HTTP_400_BAD_REQUEST)

			
class EmpidDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual manager
	""" Class based API View to display and delete specific Employee ID
	details thrugh GET and DELETE requests. Deleteion only results in deletion of 
	the concerned employee User and his rooms but retains ID instance for reuse
	"""
	
	queryset = EmployeeID.objects.all()
	serializer_class = EmployeeIDSerializer  
	lookup_field = 'emp_id'
		
	def delete(self, request, emp_id):
		try:
			empid_inst = EmployeeID.objects.get(emp_id=emp_id)
			user = empid_inst.assignee
		except User.DoesNotExist:
			return Response({"message": "Employee ID not found."}, status=404)	
		else:	
			user.delete()
			empid_inst.assignee = None
			empid_inst.save()         # Delete the employee, unassign employee ID, but the ID is AVAILABLE FOR REUSE
			return Response({"message": "Emplyee Deleted. ID Avalaible for Re-Assignment"}, status=204)	
										
    
class RoomHandler(generics.RetrieveAPIView):
	""" Class based API View to display and delete specific Room
	details through GET and DELETE requests
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = Room.objects.all()
	
	def get(self, request, format=None):
		rooms = Room.objects.all()
		serializer = RoomSerializer(rooms, many=True, context={'request':request})
		return Response(serializer.data)
		
class RoomDetail(generics.RetrieveDestroyAPIView):     # Read-Only for an individual user
	""" Class based API View to display and delete specific Room
	details thrugh GET and DELETE requests
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
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
	""" Class based API View to handle listing of Slots for rooms
	through GET requests
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = Slot.objects.all()
	
	def get(self, request, format=None):
		slots = Slot.objects.all()
		serializer = SlotSerializer(slots, many=True, context={'request':request})
		return Response(serializer.data)	
		
		
class SlotDetail(generics.RetrieveDestroyAPIView):    
	""" Class based API View to display and delete specific Slot
	details thrugh GET and DELETE requests
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
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
	""" Class based API View to handle listing all reservation type (past, future, etc)
	URLs through GET requests
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	
	def get(self, request, format=None):
		reserves = User.objects.filter(email=request.user.email)      # Dummy QuerySet with on Entry
		serializer = ReservationLinkSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data) 
		
        
class PastReservations(APIView):    # For a list of users
	""" Class based API View to handle listing past reservations
	through GET request
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	
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
	""" Class based API View to handle listing future reservations
	through GET requests
	"""
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	
	def get(self, request, format=None):
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())
		reserves = Reservation.objects.filter(	date__gt=today)|(	                                                 			           Reservation.objects.filter(	date=today,
        										slot__start_time__gt=now))  # All reservations in this model are "Active"
		serializer = ActiveReservationSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data) 
		              

class OngoingReservations(APIView):    # For a list of users
	""" Class based API View to handle listing currently occupied reservations
	through GET requests
	"""
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	
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
	""" Class based API View to handle listing cancelled reservations
	through GET requests
	"""
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	
	def get(self, request, format=None):
		reserves = IsolatedResData.objects.filter(status='Cancelled')
		serializer = ReservationSerializer(reserves, many=True, context={'request':request}) 
		return Response(serializer.data) 
		 		
		
class InactiveReservationDetail(generics.RetrieveAPIView):     # Read-Only for an individual user
	""" Class based API View to display individual Reservation
	trhough GET requests, either in Past or Cancelled
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = IsolatedResData.objects.all()
	serializer_class = ReservationSerializer    
	lookup_field = 'id'  
	 
    
class ActiveReservationManage(generics.RetrieveDestroyAPIView):
	""" Class based API View to handle deletion and display of a specific Reservations
	through GET and DELETE requests
	"""
	
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = Reservation.objects.all()
	serializer_class = ActiveReservationSerializer    
	lookup_field = 'id'  
	
	def delete(self, request, id):     # Overriding the default delete method 
		this_reserve = self.queryset.get(id=id)	
		# Simoultaneously setting status as Cancelled in Isolated Reservation Data
		# This is done using a pre_delete signal attached to Reservation model
		this_reserve.delete()
		return Response({"message": "Reservation has been deleted."}, status=204)	
	          	
		                  

    
    
     
