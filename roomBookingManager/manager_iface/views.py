from django import forms
from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from roomBookingManager.decorators import group_required, anonymous_required
from datetime import datetime
from users.models import Manager
from customer_iface.models import Reservation, IsolatedResData
from .forms import RoomCreationForm, SlotCreationForm
from .models import Room, Slot


@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')
class CreateRoom(View):
	form = RoomCreationForm()
	template = 'manager_iface/DisplayForm.html'
	
	def roomno_exists(self,value):
		all_roomnos = tuple(map(str,Room.objects.all()))
		if(value in all_roomnos):
			return True
		else:
			return False
	
	def post(self,request,*args,**kwargs):
		self.form = RoomCreationForm(request.POST)
		try:
			if(self.form.is_valid()):	
				if(self.roomno_exists(self.form.cleaned_data['room_no'])):
					raise ValueError("Room Number Already Exists")	
				   
				new_room = Room()
				new_room.room_no = self.form.cleaned_data['room_no']
				new_room.advance_period = self.form.cleaned_data['advance_period']
				new_room.description = self.form.cleaned_data['description']
				new_room.manager = Manager.objects.filter(instance=request.user)[0]   
				new_room.save()			
				
				messages.add_message(request, messages.SUCCESS, "Room Created Successfully!")	
				return HttpResponseRedirect(reverse('RoomCreation'))
				
			else:
				raise ValueError("Unknow Error Occurred!")
				
		except ValueError as prob:
			messages.add_message(request, messages.ERROR, prob)
			return HttpResponseRedirect(reverse('home'))
						
	
	def get(self,request,*args,**kwargs):
		cont = dict()
		cont['form'] = self.form
		cont['prompt'] = "Create New Room"
		return render(request, self.template, context=cont)


@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')	
class CreateSlot(View):
	template = 'manager_iface/DisplayForm.html'
	
	def own_rooms(self,request):
		this_manager = Manager.objects.filter(instance=request.user)[0]
		return list(Room.objects.filter(manager=this_manager))
	
	def slot_intrudes(self,this_room,start,end):
		start = datetime.time(datetime.strptime(start,"%H:%M"))
		end = datetime.time(datetime.strptime(end,"%H:%M"))
		check_slots = Slot.objects.filter(room=this_room)
		for slot in check_slots:
			if(slot.start_time<start<slot.end_time):
				return True
			elif(slot.start_time<end<slot.end_time):
				return True
			elif(start<slot.start_time<end):
				return True
			elif(start<slot.end_time<end):
				return True
			elif(self.duplicate_slot(slot,start,end)):
				return True	
		return False		
				
	def duplicate_slot(self,existing_slot,start,end):
		if(existing_slot.start_time==start):
			if(existing_slot.end_time==end):
				return True
		return False						
	
	def post(self,request,*args,**kwargs):
		rooms_to_disp = self.own_rooms(request)
		choices = tuple(zip(rooms_to_disp,map(str,rooms_to_disp)))
		self.form = SlotCreationForm(request.POST, choices=choices)
		# Necessary to refill choices since the form is Re-Instantiated here
		try:
			if(self.form.is_valid()):	
				slot_start = self.form.cleaned_data['start_time'].strftime("%H:%M")  
				# In required format
				slot_end = self.form.cleaned_data['end_time'].strftime("%H:%M") 
				if(slot_start>=slot_end):
					raise ValueError("Start Time should be before End Time")
				if(self.slot_intrudes(self.form.cleaned_data['room'],slot_start,slot_end)):
					raise ValueError("Slot timings clash with another!")				
				target_room = Room.objects.filter(room_no=str(self.form.cleaned_data['room']))[0]        
				new_slot = Slot()
				new_slot.room = target_room
				new_slot.start_time = slot_start
				new_slot.end_time = slot_end
				new_slot.save()			
				
				messages.add_message(request, messages.SUCCESS, "Slot Created Successfully!")	
				return HttpResponseRedirect(reverse('SlotCreation'))
				
			else:
				raise ValueError("Invalid Form!")
				
		except ValueError as prob:
			messages.add_message(request, messages.ERROR, prob)
			return HttpResponseRedirect(reverse('SlotCreation'))
						
	
	def get(self,request,*args,**kwargs):
		rooms_to_disp = self.own_rooms(request)
		if(rooms_to_disp):
			cont = dict()
			room_choices = tuple(zip(rooms_to_disp,map(str,rooms_to_disp)))
			self.form = SlotCreationForm(choices=room_choices)
			# Exploiting the deep-copied field attribute of Form Class, that was created using its MetaClass
			cont['form'] = self.form
			cont['prompt'] = "Create New Slot"
			return render(request, self.template, context=cont)	
		else:
			messages.add_message(request, messages.ERROR, "No Rooms Under Your Control!")
			return HttpResponseRedirect(reverse('RoomCreation'))
	

@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')
class ManageRooms(View):
	get_template = 'manager_iface/ManageRooms.html'
	post_template = 'manager_iface/ConfirmDeletion.html'
	
	def post(self,request,*args,**kwargs):
		if(request.POST['action']=="Delete"):
			this_room = Room.objects.filter(room_no=request.POST['roomNo'])[0]
			time_now = datetime.time(datetime.now())
			date_now = datetime.date(datetime.now())
			t = list()
			for i in list(Reservation.objects.all()):
				t.append(i.date)
			reserves = Reservation.objects.filter(
											room=this_room, 
											date__gt=date_now
										  )|Reservation.objects.filter(
										 	room=this_room, 
											date=date_now,
											slot__start_time__gte=time_now
										  )
			# To provide hyperlinks to customer profile
			cust_links = [(i.customer.instance.name,                 
						i.customer.instance.email) for i in reserves]
			disp_data = [(i.date,
                     	i.slot.start_time.strftime("%H:%M"),
                     	i.slot.end_time.strftime("%H:%M"),                     	
						i.room.manager.instance.name) for i in reserves]
			reserves = list(zip(cust_links,disp_data))			
						
			cont = dict()
			cont['display'] = bool(len(reserves))
			cont['roomNo'] = this_room.room_no
			cont['reserves'] = reserves	          
			cont['dispData'] = disp_data
			cont['object'] = "Room"
			cont['effect'] = "cancelled"
			cont['button'] = "Delete"
			
			return render(request,self.post_template,context=cont)
		
		else:
			return HttpResponseRedirect(reverse('ManageRooms'))								
	
	def get(self,request,*args,**kwargs):	
		this_manager = Manager.objects.filter(instance=request.user)[0]
		own_rooms = Room.objects.filter(manager=this_manager)
		form_row = [('a'+str(x+1),'b'+str(x+1)) for x in range(len(own_rooms))]
		data_rooms = [(own_rooms[i].room_no,
                     own_rooms[i].advance_period,
                     own_rooms[i].description) for i in range(len(own_rooms))]
		own_rooms = list(zip(form_row,data_rooms))             
                   
		other_rooms = Room.objects.all().exclude(manager=this_manager)
		form_row = ['c'+str(x+1) for x in range(len(other_rooms))]   
		data_rooms = [(other_rooms[i].room_no,
                     other_rooms[i].advance_period,
                     other_rooms[i].description) for i in range(len(other_rooms))]
		manager_links = [[i.manager.instance.name,                 
						i.manager.instance.email] for i in other_rooms]
		other_rooms =  list(zip(form_row,data_rooms,manager_links))            
                     
		cont = dict()   
		cont['ownRooms'] = own_rooms
		cont['otherRooms'] = other_rooms
		cont['display'] = (bool(len(own_rooms)),bool(len(other_rooms)))
        
		return render(request,self.get_template,context=cont) 	
		

@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')		
class DeleteRoom(View):
	
	def post(self,request,*args,**kwargs):
		target_roomno = list(request.POST.keys())[1]
		# Affected reservations
		# Getting and Modifying the IsolatedDatabase Accordingly through a pre_delete signal
		deleted = Room.objects.filter(room_no=target_roomno).delete()
		messages.add_message(request, messages.SUCCESS, "Deleted Successfully.Email notification to customers(if any) was attempted")
		return HttpResponseRedirect(reverse('ManageRooms'))			
		

@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')		
class ManageSlots(View):
	template = 'manager_iface/ManageSlots.html'
	res_template = 'manager_iface/ConfirmDeletion.html'
	
	def post(self,request,*args,**kwargs):	
		if(request.POST['action']=="View Slots"):	
			this_manager = Manager.objects.filter(instance=request.user)[0]
			this_room = Room.objects.filter(room_no=request.POST['roomNo'])[0]
			
			slots = Slot.objects.filter(room=this_room)
			form_row = [('a'+str(x+1),'b'+str(x+1)) for x in range(len(slots))]  
			serials = [x+1 for x in range(len(slots))]
			slots_data = [(serials[i],
		              	slots[i].start_time.strftime("%H:%M"),
		              	slots[i].end_time.strftime("%H:%M")) for i in range(len(slots))]
			slots = list(zip(form_row,slots_data))           	
		                 
			cont = dict()   
			cont['slots'] = slots
			cont['ownRoom'] = (this_room.manager==this_manager)
			cont['roomNo'] = this_room.room_no
			cont['display'] = bool(len(slots))
		    
			return render(request,self.template,context=cont)  	
		
		elif(request.POST['action'] in ("Delete","Modify")):		
			room_no = request.POST['roomNo']
			this_room = Room.objects.filter(room_no=room_no)[0]
			time_now = datetime.time(datetime.now())
			date_now = datetime.date(datetime.now())
			start_time = datetime.time(datetime.strptime(request.POST['start'],"%H:%M"))
			this_slot = Slot.objects.filter(room=this_room, start_time=start_time)[0]
			
			reserves = Reservation.objects.filter(
											slot=this_slot, 
											date__gt=date_now
										  )|Reservation.objects.filter(
										 	slot=this_slot, 
											date=date_now,
											slot__start_time__gte=time_now
										  )							  
			# To provide hyperlinks to customer profile
			cust_links = [(i.customer.instance.name,                 
						i.customer.instance.email) for i in reserves]
			disp_data = [(i.date,
                     	i.slot.start_time.strftime("%H:%M"),
                     	i.slot.end_time.strftime("%H:%M"),                     	
						i.room.manager.instance.name) for i in reserves]
			reserves = list(zip(cust_links,disp_data))			
						
			cont = dict()
			cont['display'] = bool(len(reserves))
			cont['roomNo'] = this_room.room_no
			cont['start'] = this_slot.start_time.strftime("%H:%M")
			cont['reserves'] = reserves	          
			cont['dispData'] = disp_data
			cont['object'] = "Slot"
			if(request.POST['action']=="Delete"):
				cont['effect'] = "cancelled"
				cont['button'] = "Delete"
			else:
				cont['effect'] = "altered"	
				cont['button'] = "Modify"
			
			return render(request,self.res_template,context=cont)
			
	def get(self,request,*args,**kwargs):
		messages.add_message(request, messages.ERROR, "Select a room first")
		return HttpResponseRedirect(reverse('ManageRooms'))


@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')		
class ModifySlot(View):
	template = 'manager_iface/DisplayForm.html'	
	
	def get_room(self,roomno):
		return list(Room.objects.filter(room_no=roomno))[0]	
	def slot_intrudes(self,this_room,start,end):
		start = datetime.time(datetime.strptime(start,"%H:%M"))
		end = datetime.time(datetime.strptime(end,"%H:%M"))
		check_slots = Slot.objects.filter(room=this_room)
		ctr = 0               # The new slot can coincide with the slot being replaced
		for slot in check_slots:
			if(slot.start_time<start<slot.end_time):
				ctr += 1
			elif(slot.start_time<end<slot.end_time):
				ctr += 1
			elif(start<slot.start_time<end):
				ctr += 1
			elif(start<slot.end_time<end):
				ctr += 1
			elif(self.duplicate_slot(slot,start,end)):
				ctr += 1
			if(ctr>1):
				return True	
		return False						
	def duplicate_slot(self,existing_slot,start,end):
		if(existing_slot.start_time==start):
			if(existing_slot.end_time==end):
				return True
		return False							
	
	def post(self,request,*args,**kwargs):
		if('roomNo' in request.POST.keys()):
			this_roomno = request.POST['roomNo']
			this_start = request.POST['start']
			this_slot = Slot.objects.filter(room__room_no=this_roomno, 
											start_time=this_start)[0]		
			
			room_choices = [(self.get_room(this_roomno), this_roomno)]								
			self.form = SlotCreationForm(for_modification=True,
											room_inst=self.get_room(this_roomno),
											slot_inst=this_slot,
											choices = room_choices
											)
																
			cont = dict()			
			#Setting existing values for the slot
			'''self.form.fields['room'].choices = [(self.get_room(this_roomno), this_roomno)]
			self.form.fields['room'].initial = this_roomno
			self.form.fields['room'].disabled = True
			self.form.fields['start_time'].initial = this_slot.start_time.strftime("%H:%M")
			self.form.fields['end_time'].initial = this_slot.end_time.strftime("%H:%M")	'''		
			# Exploiting the deep-copied field attribute of Form Class, that was created using its MetaClass
			cont['form'] = self.form
			cont['prompt'] = "Modify Slot"
			cont['roomNo'] = this_roomno
			cont['start'] = this_start
			# Explicitly posting the room no. since field is disabled
			cont['extra'] = True
			return render(request, self.template, context=cont)				
		else:
			rooms = Room.objects.all()
			room_choices = list()
			for i in list(rooms):
				room_choices.append((i, i.room_no))
			self.form = SlotCreationForm(request.POST, choices=room_choices)
			this_roomno = request.POST['room']	
			this_start = request.POST['start']    #OLD DATA - BEFORE MODIFICATION
			this_slot = Slot.objects.filter(room__room_no=this_roomno, 
											start_time=this_start)[0]  
			# Exploiting the deep-copied field attribute of Form Class, that was created using its MetaClass
			# Necessary to refill choices since the form is Re-Instantiated here
			try:
				if(self.form.is_valid()):						
					slot_start = self.form.cleaned_data['start_time'].strftime("%H:%M")  # In required format
					slot_end = self.form.cleaned_data['end_time'].strftime("%H:%M")  # In required format
					if(slot_start>=slot_end):
						raise ValueError("Start Time should be before End Time")
					if(self.slot_intrudes(self.form.cleaned_data['room'],slot_start,slot_end)):
						raise ValueError("Slot timings clash with another!")
					# the IsolatedDatabase is modified accordingly using signals
					# Modifying slots	
					
					"""If a slot is changed in such a way that the new start_time of the 
					slot is before the present time and its old start_time was after present_time
					Then the corresponding reservations today would have moved from the future into the
					past! Such reservations have to be deleted and not modified
					"""
					
					now = datetime.time(datetime.now())
					check = datetime.time(datetime.strptime(slot_start,"%H:%M"))
					if(check<now):
						today = datetime.date(datetime.now())
						affected_res = Reservation.objects.filter(
										 			slot=this_slot, 
													date=today,
													slot__start_time__gte=now)
						for i in list(affected_res):
							i.delete()	# IsoResData is automatically set to cancelled through a signal						
					
					# Modifying other slots
					old_start = this_slot.start_time
					this_slot.start_time = slot_start
					this_slot.end_time = slot_end
					this_slot.save(old_start_time=old_start, room_no=this_roomno)									  	
					# Additional keyword arguments are sent to the post_save signals to modify IsoResData
					messages.add_message(request, messages.SUCCESS, "Slot Updated Successfully! Email notification to Customer was attempted")	
					return HttpResponseRedirect(reverse('ManageRooms'))
					
				else:
					raise ValueError("Invalid Form!")
					
			except ValueError as prob:
				messages.add_message(request, messages.ERROR, prob)
				return HttpResponseRedirect(reverse('ManageRooms'))
				

@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')		
class DeleteSlot(View):
	
	def post(self,request):
		target_roomno = request.POST['roomNo']		
		start_time = datetime.time(datetime.strptime(request.POST['start'],"%H:%M"))
		target_slot = Slot.objects.filter(room__room_no=target_roomno, start_time=start_time)[0]
		# Affected reservations
		# Getting and Modifying the IsolatedDatabase Accordingly
		# No two slots will have the same start time
		deleted = target_slot.delete()
		messages.add_message(request, messages.SUCCESS, "Deleted Successfully. Email notification to Customer was attempted")
		return HttpResponseRedirect(reverse('ManageRooms'))	
		

@method_decorator(group_required('ManagerPrivilege',redirect_view='Login'), name='dispatch')
class ViewReservations(View):
	template = "manager_iface/ViewBookings.html"

	def get(self,request,*args,**kwargs):
                         
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())                         
		future_res = list(IsolatedResData.objects.filter(date__gt=today,
        												status="Active") |	                                                 			                IsolatedResData.objects.filter(date=today,
        												start_time__gt=now,
        												status="Active"))                
        # Past Bookings                  
		past_res = list(IsolatedResData.objects.filter(date__lt=today,
														status="Active") |	                                                 			                IsolatedResData.objects.filter(date=today,
														end_time__lte=now,
														status="Active"))
		present_res = list(IsolatedResData.objects.filter(date=today,
														start_time__lt=now,
														end_time__gte=now,
														status="Active"))	
		can_res = list(IsolatedResData.objects.filter(status="Cancelled"))
		
		manager_links = [(i.manager_name,                 
						i.manager_email) for i in future_res]
		cust_links = [(i.cust_name,                 
						i.cust_email) for i in future_res]				
		future_data = [(i.room_no,
						i.date.strftime("%Y-%m-%d"),
						i.start_time.strftime("%H:%M"),
						i.end_time.strftime("%H:%M"),
						i.status) for i in future_res]
		future_res = list(zip(manager_links,cust_links,future_data))	
				
		manager_links = [(i.manager_name,                 
						i.manager_email) for i in past_res]
		cust_links = [(i.cust_name,                 
						i.cust_email) for i in past_res]	
		past_data = [[i.room_no,
						i.date.strftime("%Y-%m-%d"),
						i.start_time.strftime("%H:%M"),
						i.end_time.strftime("%H:%M"),
						i.status] for i in past_res]
		past_res = list(zip(manager_links,cust_links,past_data))					
						
		manager_links = [(i.manager_name,                 
						i.manager_email) for i in can_res]
		cust_links = [(i.cust_name,                 
						i.cust_email) for i in can_res]				
		can_data = [(i.room_no,
						i.date.strftime("%Y-%m-%d"),
						i.start_time.strftime("%H:%M"),
						i.end_time.strftime("%H:%M"),
						i.status) for i in can_res]
		can_res = list(zip(manager_links,cust_links,can_data))	
				
		manager_links = [(i.manager_name,                 
						i.manager_email) for i in present_res]
		cust_links = [(i.cust_name,                 
						i.cust_email) for i in present_res]	
		present_data = [[i.room_no,
						i.date.strftime("%Y-%m-%d"),
						i.start_time.strftime("%H:%M"),
						i.end_time.strftime("%H:%M"),
						i.status] for i in present_res]
		present_res = list(zip(manager_links,cust_links,present_data))									
						
		for data in past_data:
			if(data[4]=="Active"):
				data[4]="Used"     # Active rooms of the past, were occupied already				
		past_res = list(zip(manager_links,past_data))			
		cont = dict()			
		cont['past'] = past_res
		cont['future'] = future_res
		cont['present'] = present_res
		cont['cancel'] = can_res
		cont['display'] = (bool(len(present_res)),bool(len(future_res)),bool(len(past_res)),bool(len(can_res)))
		return render(request,self.template,context=cont)
		                  		
		
		


