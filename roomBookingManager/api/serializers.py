from rest_framework import serializers
from users.models import User, Customer, Manager
from manager_iface.models import Room, Slot
from customer_iface.models import IsolatedResData, Reservation
from django.contrib.auth.models import Group
from django.urls import reverse
from urllib.parse import urljoin, urlparse, urlunparse
from django.contrib.sites.models import Site
from datetime import datetime


class UserSerializer(serializers.ModelSerializer):
		
	# Only fields that require an explicit definition to display have to be mentioned here	
	url = serializers.HyperlinkedIdentityField(view_name='user-detail',lookup_field='id')
	user_type = serializers.SerializerMethodField()	
	user_type_desc = serializers.SerializerMethodField(method_name="get_user_detail")
	
	class Meta:
		model = User
		fields = ['id','url','user_type','user_type_desc','email','name']		
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
			print(user.name)
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
					

class CustomerSerializer(serializers.HyperlinkedModelSerializer):
	instance = UserSerializer(read_only=True)      
	# Defining a METHOD FIELD to generate URL based on 
	# User class since primary key for customer is an object
	url = serializers.SerializerMethodField()		
	# CHANGE TO READ_WRITE	
	future_reservations = serializers.SerializerMethodField()
	past_reservations = serializers.SerializerMethodField()
	cancelled_reservations = serializers.SerializerMethodField()
	
	def __init__(self,*args,**kwargs):
		fields = kwargs.pop('fields',None)
		super(CustomerSerializer, self).__init__(*args,**kwargs)
		if(fields):
			self.fields = fields				
	
	class Meta:
		model = Customer
		fields = ['url','instance','future_reservations','past_reservations','cancelled_reservations']
	
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

	url = serializers.SerializerMethodField()
	instance = UserSerializer(read_only=True)  
	# Defining a METHOD FIELD to generate URL based on 
	# User class since primary key for customer is an object
	rooms = serializers.SerializerMethodField()
	# CHANGE TO READ_WRITE	
	
	def __init__(self,*args,**kwargs):
		fields = kwargs.pop('fields',None)
		super(ManagerSerializer, self).__init__(*args,**kwargs)
		if(fields):
			self.fields = fields		
	
	class Meta:
		model = Manager
		fields = ['url','instance','rooms']
		
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

	url = serializers.SerializerMethodField()
	instance = UserSerializer(read_only=True)  
	# Defining a METHOD FIELD to generate URL based on 
	# User class since primary key for customer is an object
	# CHANGE TO READ_WRITE	
	
	def __init__(self,*args,**kwargs):
		fields = kwargs.pop('fields',None)
		super(ManagerSerializer, self).__init__(*args,**kwargs)
		if(fields):
			self.fields = fields		
	
	class Meta:
		model = Manager
		fields = ['url','instance']
		
	def get_url(self, adm):
		user_id = adm.instance.id
		rel_url = reverse('user-detail',args=[user_id])   # Return relative URL for WebSite
		rel_url = rel_url.replace('user','admin')
		scheme = self.context['request'].META['wsgi.url_scheme']
		netloc = self.context['request'].META['HTTP_HOST']
		domain = urlunparse((scheme,netloc,'/','','',''))
		url = urljoin(domain,rel_url)
		return url
				
class RoomSerializer(serializers.HyperlinkedModelSerializer):
	
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

	room = RoomSerializer(read_only=True)
	url = serializers.HyperlinkedIdentityField(view_name='slot-detail',lookup_field='id')
	
	class Meta:
		model = Slot
		fields = ['id','url', 'start_time', 'end_time', 'room']	
				
class ReservationLinkSerializer(serializers.Serializer):
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
			
	
		
			
			
