"""Module to implement serializers to organise data to be rendered
in response to an API Query"""

from rest_framework import serializers
from users.models import User, Customer, Manager, EmployeeID, Admin
from users.constants import EMPLOYEE_PREFIXES
from manager_iface.models import Room, Slot
from customer_iface.models import IsolatedResData, Reservation
from django.contrib.auth.models import Group
from django.urls import reverse
from urllib.parse import urljoin, urlparse, urlunparse
from django.contrib.sites.models import Site
from django.core.validators import validate_email
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ValidationError   # raised by validate_email
from datetime import datetime

"""VALIDATORS """

class IsEmailValid(object):
	"""Custom class based validator to validate email serializer data
	"""
	
	def __init__(self, value):
		self.value = value
		
	def __call__(self):
		try:
			validate_email(self.value)
		except ValidationError:
			mess = "Email should be valid"
			raise serializers.ValidationError(mess)	
			
			
class IsNameValid(object):
	"""Custom class based validator to validate name serializer data
	"""		
	
	def __init__(self, value):
		self.value = value
		
	def __call__(self):
		for k in self.value:
			if k.isdigit():
				mess = "Name cannot contain digits"
				raise serializers.ValidationError(mess)
			
				
class IsGenderValid(object):
	"""Custom class based validator to validate gender serializer data
	"""		
	
	def __init__(self, value):
		self.value = value
		
	def __call__(self):
		if(self.value not in ['M','F']):
			mess = "Gender must be M/F"
			raise serializers.ValidationError(mess)
			
			
class IsPhoneValid(object):
	"""Custom class based validator to validate phone serializer data
	"""		
	
	def __init__(self, value):
		self.value = value
		
	def __call__(self):
		if len(self.value)!=10:
			mess = "Mobile Number must be 10 digits"
			raise serializers.ValidationError(mess)
		for k in self.value:
			if not k.isdigit():
				mess = "Only Numbers Allowed in phone number"
				raise serializers.ValidationError(mess)
				

class IsEmpTypeValid(object):	
	"""Custom class based validator to validate employee type serializer data
	"""		
	
	def __init__(self, value):
		self.value = value
		
	def __call__(self):
		if(value not in EMPLOYEE_PREFIXES.keys()):
			mess = "Invalid employee type / designation"
			raise serializers.ValidationError(mess)	
		
		

""" SERIALIZERS """

class UserSerializer(serializers.ModelSerializer):
	"""Class based serializer to serialize User data for 
	user listing, deletion, creation, detail API queries
	"""
		
	# Only fields that require an explicit definition to display have to be mentioned here	
	url = serializers.HyperlinkedIdentityField(view_name='user-detail',lookup_field='id', read_only=True)
	user_type = serializers.SerializerMethodField(read_only=True)	
	user_type_desc = serializers.SerializerMethodField(method_name="get_user_detail", read_only=True)
	email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(),
																message="Email already exists"),
											  IsEmailValid], required=True)
	name = serializers.CharField(max_length=20, validators=[IsNameValid], required=True)	
	is_staff = serializers.HiddenField(default=False)
	is_superuser = serializers.HiddenField(default=False)
	password = serializers.HiddenField(default="")    # Dummy placeholder for accepting password in API request
	
	def create(self, validated_data):
		user = User.objects.create(**validated_data)
		user.set_password(validated_data['password'])
		user.save()
		return user
	
	class Meta:
		model = User
		fields = ['id','url','user_type','user_type_desc','email','name','is_staff','is_superuser','password']		
		lookup_field = 'id'
		
	def get_user_type(self, user):
		targetGroup=Group.objects.get(user=user).name
		if(targetGroup=="CustomerPrivilege"):
			return 'customer'
		elif(targetGroup=="ManagerPrivilege"):
			return 'manager'
		elif(targetGroup=="AdminPrivilege"):
			return 'admin'
		else:
			return None	 
			
	def get_user_detail(self, user): 
		user_type = self.get_user_type(user) 
		if(user_type=='customer'):
			return {'gender':user.customer.gender,
					'phone':user.customer.phone}
		elif(user_type=='manager'):
			return {'emp_id':user.manager.emp_id.emp_id,
					'gender':user.manager.gender,
					'phone':user.manager.phone}
		elif(user_type=='admin'):
			return {'emp_id':user.admin.emp_id.emp_id}
		else:
			return {"ERROR":"Unknown User Type"}				
				

class CustomerSerializer(serializers.ModelSerializer):
	"""Class based serializer to serialize Customer data for 
	listing, deletion, creation, detail API queries
	"""

	instance = UserSerializer(read_only=True)      
	# Defining a METHOD FIELD to generate URL based on 
	# User class since primary key for customer is an object
	url = serializers.SerializerMethodField(read_only=True)		
	gender = serializers.CharField(max_length=1, validators=[IsGenderValid], required=True)
	phone = serializers.CharField(max_length=10, validators=[IsPhoneValid], required=True)
	# CHANGE TO READ_WRITE	
	future_reservations = serializers.SerializerMethodField(read_only=True)
	past_reservations = serializers.SerializerMethodField(read_only=True)
	cancelled_reservations = serializers.SerializerMethodField(read_only=True)
	
	def __init__(self,*args,**kwargs):
		fields = kwargs.pop('fields',None)
		super(CustomerSerializer, self).__init__(*args,**kwargs)
		if(fields):
			self.fields = fields				
	
	class Meta:
		model = Customer
		fields = ['url','instance','future_reservations','past_reservations','cancelled_reservations',
					'gender','phone']
	
	def get_url(self,cust):
		user_id = cust.instance.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','cust')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
	
	def get_past_reservations(self, cust):
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())
		reserves = list(IsolatedResData.objects.filter(cust_email=cust.instance.email,
        												date__lt=today,
        												status="Active") |	                                                 			                IsolatedResData.objects.filter(cust_email=cust.instance.email,
        												date=today,
        												start_time__lte=now,
        												status="Active"))	
		ret = dict()
		for i in range(len(list(reserves))):
			rel_url = reverse('reserve-detail',args=[reserves[i].id])   # Return relative URL for WebSite
			scheme = self.context['request'].META['wsgi.url_scheme']
			netloc = self.context['request'].META['HTTP_HOST']
			domain = urlunparse((scheme,netloc,'/','','',''))
			url = urljoin(domain,rel_url)	
			sub_dict = dict()
			sub_dict['room'] = reserves[i].room_no
			sub_dict['date'] = reserves[i].date
			sub_dict['start_time'] = reserves[i].start_time
			sub_dict['end_time'] = reserves[i].end_time
			sub_dict['reservation_url'] = url
			ret[i+1] = sub_dict
		return ret	
		
	def get_cancelled_reservations(self, cust):
		reserves = list(IsolatedResData.objects.filter(cust_email=cust.instance.email,
        												status="Cancelled"))	
		ret = dict()
		for i in range(len(list(reserves))):
			rel_url = reverse('reserve-detail',args=[reserves[i].id])   # Return relative URL for WebSite
			scheme = self.context['request'].META['wsgi.url_scheme']
			netloc = self.context['request'].META['HTTP_HOST']
			domain = urlunparse((scheme,netloc,'/','','',''))
			url = urljoin(domain,rel_url)	
			sub_dict = dict()
			sub_dict['room'] = reserves[i].room_no
			sub_dict['date'] = reserves[i].date
			sub_dict['start_time'] = reserves[i].start_time
			sub_dict['end_time'] = reserves[i].end_time
			sub_dict['reservation_url'] = url
			ret[i+1] = sub_dict
		return ret	
		
	def get_future_reservations(self, cust):
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())
		reserves = list(Reservation.objects.filter(customer__instance__email=cust.instance.email,
        												date__gt=today) |	                                                 			                Reservation.objects.filter(customer__instance__email=cust.instance.email,
        												date=today,
        												slot__start_time__gte=now))	
        				# ALL reservations in this model will be "Active"
		ret = dict()
		for i in range(len(reserves)):
			rel_url = reverse('reserve-manage',args=[reserves[i].id])   # Return relative URL for WebSite
			scheme = self.context['request'].META['wsgi.url_scheme']
			netloc = self.context['request'].META['HTTP_HOST']
			domain = urlunparse((scheme,netloc,'/','','',''))
			url = urljoin(domain,rel_url)	
			sub_dict = dict()
			sub_dict['room'] = reserves[i].room.room_no
			sub_dict['date'] = reserves[i].date
			sub_dict['start_time'] = reserves[i].slot.start_time
			sub_dict['end_time'] = reserves[i].slot.end_time
			sub_dict['reservation_url'] = url
			ret[i+1] = sub_dict
		return ret		
				        												
		
class ManagerSerializer(serializers.HyperlinkedModelSerializer):
	"""Class based serializer to serialize Manager data for 
	listing, deletion, creation, detail API queries
	"""

	url = serializers.SerializerMethodField(read_only=True)
	instance = UserSerializer(read_only=True)  
	# Defining a METHOD FIELD to generate URL based on 
	# User class since primary key for customer is an object
	rooms = serializers.SerializerMethodField(read_only=True)	
	gender = serializers.CharField(max_length=1, validators=[IsGenderValid], required=True)
	phone = serializers.CharField(max_length=10, validators=[IsPhoneValid], required=True)
	emp_id = serializers.HiddenField(default=EmployeeID())
	# CHANGE TO READ_WRITE	
	
	def __init__(self,*args,**kwargs):
		fields = kwargs.pop('fields',None)
		super(ManagerSerializer, self).__init__(*args,**kwargs)
		if(fields):
			self.fields = fields		
	
	class Meta:
		model = Manager
		fields = ['url','instance','rooms','gender','phone','emp_id']
		
	def get_url(self, man):
		user_id = man.instance.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','manager')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
		
	def get_rooms(self, manager):
		rooms = Room.objects.filter(manager=manager)
		ret = dict()
		for i in range(len(list(rooms))):
			rel_url = reverse('room-detail',args=[rooms[i].room_no])   # Return relative URL for WebSite
			scheme = self.context['request'].META['wsgi.url_scheme']
			netloc = self.context['request'].META['HTTP_HOST']
			domain = urlunparse((scheme,netloc,'/','','',''))
			url = urljoin(domain,rel_url)			
			sub_dict = dict()
			sub_dict['room_no'] = rooms[i].room_no
			sub_dict['advance_period'] = rooms[i].advance_period
			sub_dict['room_url'] = url
			ret[i+1] = sub_dict
		return ret	
			
class AdminSerializer(serializers.HyperlinkedModelSerializer):
	"""Class based serializer to serialize Manager data for 
	listing, deletion, creation, detail API queries
	"""

	url = serializers.SerializerMethodField(read_only=True)
	instance = UserSerializer(read_only=True)  
	emp_id = serializers.HiddenField(default=EmployeeID())
	# Defining a METHOD FIELD to generate URL based on 
	# User class since primary key for customer is an object
	# CHANGE TO READ_WRITE	
	
	def __init__(self,*args,**kwargs):
		fields = kwargs.pop('fields',None)
		super(AdminSerializer, self).__init__(*args,**kwargs)
		if(fields):
			self.fields = fields		
	
	class Meta:
		model = Admin
		fields = ['url','instance','emp_id']
		
	def get_url(self, adm):
		user_id = adm.instance.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','admin')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
		
		
	
class EmployeeIDSerializer(serializers.HyperlinkedModelSerializer):
	"""Class based serializer to serialize Employee ID data for 
	listing, deletion, creation, detail API queries
	"""
	
	url = serializers.SerializerMethodField(read_only=True)
	emp_id = serializers.CharField(read_only=True)
	emp_type= serializers.CharField(validators=[IsEmpTypeValid])
	creator = UserSerializer(read_only=True)
	assignee = UserSerializer(read_only=True, default=None)
	
	class Meta:
		model = EmployeeID
		fields = ['url', 'emp_id', 'emp_type', 'creator', 'assignee']
		
	def get_url(self, empid_inst):
		empid = empid_inst.emp_id
		rel_url = reverse('empid-detail',args=[empid])   # Return relative URL for WebSite
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url	
			
				
class RoomSerializer(serializers.HyperlinkedModelSerializer):
	"""Class based serializer to serialize Room data for 
	user listing, deletion, detail API queries
	"""
	
	room_url = serializers.HyperlinkedIdentityField(view_name='room-detail',lookup_field='room_no')
	manager = ManagerSerializer(read_only=True)
	slots = serializers.SerializerMethodField()
	
	class Meta:
		model = Room
		fields = ['room_url', 'room_no', 'slots', 'manager', 'advance_period', 'description']
	
	def get_slots(self, room):
		slots = Slot.objects.filter(room=room).order_by('start_time')	
		ret = dict()
		for i in range(len(list(slots))):
			sub_dict = dict()
			sub_dict['start_time'] = slots[i].start_time
			sub_dict['end_time'] = slots[i].end_time
			ret[i+1] = sub_dict
		return ret		
		
class SlotSerializer(serializers.HyperlinkedModelSerializer):
	"""Class based serializer to serialize Slot data for 
	user listing, deletion detail API queries
	"""
	
	room = RoomSerializer(read_only=True)
	url = serializers.HyperlinkedIdentityField(view_name='slot-detail',lookup_field='id')
	
	class Meta:
		model = Slot
		fields = ['id','url', 'start_time', 'end_time', 'room']	
		
				
class ReservationLinkSerializer(serializers.Serializer):
	"""Class based serializer to serialize Reservation data for 
	user listing, deletion, detail API queries
	"""

	future_reservations_url = serializers.SerializerMethodField()
	past_reservations_url = serializers.SerializerMethodField()
	occupied_reservations_url = serializers.SerializerMethodField()
	cancelled_reservations_url = serializers.SerializerMethodField()	
	
	class Meta:
		fields = ['future_reservations_url', 'past_reservations_url', 
					'occupied_reservations_url', 'cancelled_reservations_url']		
		
	def get_future_reservations_url(self, dummy):
		rel_url = reverse('future-reserves')   # Return relative URL for WebSite
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
		
	def get_past_reservations_url(self, dummy):
		rel_url = reverse('past-reserves')   # Return relative URL for WebSite
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
	
	def get_occupied_reservations_url(self, dummy):
		rel_url = reverse('occupied-reserves')   # Return relative URL for WebSite
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url			
		
	def get_cancelled_reservations_url(self, dummy):
		rel_url = reverse('cancelled-reserves')   # Return relative URL for WebSite
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url		
		
class ReservationSerializer(serializers.ModelSerializer):
	"""Class based serializer to serialize Reservation data for 
	user listing, deletion, detail API queries
	"""
		
	# Only fields that require an explicit definition to display have to be mentioned here	
	url = serializers.HyperlinkedIdentityField(view_name='reserve-detail',lookup_field='id')
	room_url = serializers.SerializerMethodField()
	manager_url = serializers.SerializerMethodField()
	cust_url = serializers.SerializerMethodField()
	
	class Meta:
		model = IsolatedResData
		fields = ['id','url','room_no','room_url','manager_name','manager_url',
					'cust_name','cust_url','date','start_time','end_time','status']		
		lookup_field = 'id'
		
	def get_room_url(self, reserve):
		try:
			room = Room.objects.get(room_no=reserve.room_no	)
		except Room.DoesNotExist:
			return "ROOM DOES NOT EXIST NOW"     # Either a cancelled reservation or past reservation
		else:									  # whose room doesn't exist now 
			room_no = room.room_no
			rel_url = reverse('room-detail',args=[room_no])   # Return relative URL for WebSite
			scheme = self.context['request'].META['wsgi.url_scheme']
			netloc = self.context['request'].META['HTTP_HOST']
			domain = urlunparse((scheme,netloc,'/','','',''))
			url = urljoin(domain,rel_url)
			return url	
			
	def get_cust_url(self, reserve):
		user = User.objects.get(email=reserve.cust_email)
		user_id = user.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','cust')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
		
	def get_manager_url(self, reserve):
		user = User.objects.get(email=reserve.manager_email)
		user_id = user.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','manager')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url			
			
			
class ActiveReservationSerializer(serializers.ModelSerializer):
	"""Class based serializer to serialize Active (non-cancelled) reservation data for 
	user listing, deletion, detail API queries
	"""
		
	# Only fields that require an explicit definition to display have to be mentioned here	
	url = serializers.HyperlinkedIdentityField(view_name='reserve-manage',lookup_field='id')
	room_url = serializers.SerializerMethodField()
	manager_url = serializers.SerializerMethodField()
	cust_url = serializers.SerializerMethodField()
	room_no = serializers.SerializerMethodField()
	cust_name = serializers.SerializerMethodField()
	manager_name = serializers.SerializerMethodField()
	start_time = serializers.SerializerMethodField()
	end_time = serializers.SerializerMethodField()
	status = serializers.SerializerMethodField()
	
	class Meta:
		model = Reservation
		fields = ['id','url','room_no','room_url','manager_name','manager_url',
					'cust_name','cust_url','date','start_time','end_time','status']		
		lookup_field = 'id'
		
	def get_room_url(self, reserve):					  # whose room doesn't exist now 
		room_no = reserve.room.room_no
		rel_url = reverse('room-detail',args=[room_no])   # Return relative URL for WebSite
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url				
		
	def get_cust_url(self, reserve):
		user_id = reserve.customer.instance.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','cust')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
		
	def get_manager_url(self, reserve):
		user_id = reserve.room.manager.instance.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','manager')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url	
		
	def get_room_no(self, reserve):
		return reserve.room.room_no	
		
	def get_cust_name(self, reserve):
		return reserve.customer.instance.name
		
	def get_manager_name(self, reserve):
		return reserve.room.manager.instance.name
	
	def get_start_time(self, reserve):
		return reserve.slot.start_time
		
	def get_end_time(self, reserve):
		return reserve.slot.end_time
		
	def get_status(self, reserve):
		iso_res = IsolatedResData.objects.get(room_no=reserve.room.room_no,
												date=reserve.date,
												start_time=reserve.slot.start_time)
		return iso_res.status					
			
	
		
			
			
