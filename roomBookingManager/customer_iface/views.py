from django.shortcuts import render
from django.views import View
from datetime import datetime, timedelta
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from users.models import Customer
from manager_iface.models import Slot, Room
from .models import Reservation, IsolatedResData
from .forms import SlotFindForm

class FindSlot(View):
		form = SlotFindForm()
		template = "customer_iface/DisplaySlots.html"
		
		def sep_by_room(self,slots):
			form_row = [('a'+str(x+1)) for x in range(len(slots))] 
			slot_by_room = dict()
			for sl in range(len(slots)):
				sl_data = [slots[sl].start_time.strftime("%H:%M"),
		                   slots[sl].end_time.strftime("%H:%M")]         
				if(slots[sl].room.room_no not in slot_by_room):
					slot_by_room[slots[sl].room.room_no] = [[sl_data,form_row[sl]]]
				else:
					slot_by_room[slots[sl].room.room_no].append([sl_data,form_row[sl]])
			return slot_by_room		
		
		def slot_match(self,slot1,slot2):
			if(slot1.start_time==slot2.start_time):
				if(slot1.room.room_no==slot2.room.room_no):
					return True
			return False		
		
		def post(self,request,*args,**kwargs):
			self.form = SlotFindForm(request.POST)
			if(self.form.is_valid()):		
				date = self.form.cleaned_data['date']
				today = datetime.date(datetime.now())
				now = datetime.time(datetime.now())
				if(date==today):
					slots = list(Slot.objects.filter(start_time__gt=now)) # Exclude slots whose start_time has passed
				else:
					slots = list(Slot.objects.all())	
				res_slots =  list(map(lambda x:x.slot,list(Reservation.objects.filter(date=date))))
				avl_slots = list()
				for i in slots:
				    if(i not in res_slots):
				    	# Ensure Advance Reservation Period
				    	if(today+timedelta(days=i.room.advance_period)>=date):
				        	avl_slots.append(i)
					        
				slot_by_room = self.sep_by_room(avl_slots)			
				cont = dict()
				cont['form'] = self.form
				cont['slots'] = slot_by_room
				cont['display'] = bool(len(avl_slots))
				cont['date'] = self.form.cleaned_data['date'].strftime("%Y-%m-%d")
				return render(request,self.template,context=cont)
			else:
				messages.add_message(request, messages.ERROR, prob)
				return HttpResponseRedirect(reverse('FindSlot'))	
			
	
		def get(self,request,*args,**kwargs):		
			cont = dict()
			cont['form'] = self.form
			cont['prompt'] = "Room Reservation"
			return render(request, self.template, context=cont)
      

class ReserveSlot(View):

    def post(self,request,*args,**kwargs):
        date = datetime.date(datetime.strptime(request.POST['date'],"%Y-%m-%d"))
        room_no = request.POST['roomNo']
        start_time = request.POST['start']

        this_slot = Slot.objects.filter(room__room_no=room_no,
                                        start_time=start_time)[0]
        this_customer = Customer.objects.filter(instance=request.user)[0]
        this_room = Room.objects.filter(room_no=room_no)[0]
        new_reserve = Reservation()
        new_reserve.room = this_room
        new_reserve.slot = this_slot
        new_reserve.customer = this_customer
        new_reserve.date = date
        new_reserve.save()
        
        #Simoultaneously update the isolated reservation database
        new_iso_res = IsolatedResData()
        new_iso_res.room_no = this_room.room_no
        new_iso_res.start_time = this_slot.start_time
        new_iso_res.end_time = this_slot.end_time
        new_iso_res.cust_email = this_customer.instance.email
        new_iso_res.cust_name = this_customer.instance.name
        new_iso_res.manager_email = this_room.manager.instance.email
        new_iso_res.manager_name = this_room.manager.instance.name
        new_iso_res.date = date
        new_iso_res.status = "Active"
        new_iso_res.save()       

        messages.add_message(request,messages.SUCCESS,"Room Reserved")
        return HttpResponseRedirect(reverse('FindSlot'))

    def get(self,request,*args,**kwargs):
        return HttpRespponseRedirect(reverse('FindSlot'))


class ManageReservations(View):
	template = "customer_iface/DisplayReservations.html"

	def get(self,request,*args,**kwargs):
		today = datetime.date(datetime.now())
		now = datetime.time(datetime.now())
		this_cust = Customer.objects.filter(instance=request.user)[0]                          
		future_res = list(IsolatedResData.objects.filter(cust_email=this_cust.instance.email,
        												date__gt=today,
        												status="Active") |	                                                 			                IsolatedResData.objects.filter(cust_email=this_cust.instance.email,
        												date=today,
        												start_time__gt=now,
        												status="Active"))                
        # Past Bookings                
		past_res = list(IsolatedResData.objects.filter(cust_email=this_cust.instance.email,
        												date__lt=today,
        												status="Active") |	                                                 			                IsolatedResData.objects.filter(cust_email=this_cust.instance.email,
        												date=today,
        												start_time__lte=now,
        												status="Active"))
        # Cacelled Bookings												
		can_res = list(IsolatedResData.objects.filter(cust_email=this_cust.instance.email,
        												status="Cancelled"))	
		form_row = ['a'+str(x+1) for x in range(len(future_res))] 
		manager_links = [(i.manager_name,                 
						i.manager_email) for i in future_res]
		future_data = [(i.room_no,
						i.date.strftime("%Y-%m-%d"),
						i.start_time.strftime("%H:%M"),
						i.end_time.strftime("%H:%M"),
						i.status) for i in future_res]
						
		future_res = list(zip(manager_links,future_data,form_row))			
		manager_links = [(i.manager_name,                 
						i.manager_email) for i in past_res]
		past_data = [[i.room_no,
						i.date.strftime("%Y-%m-%d"),
						i.start_time.strftime("%H:%M"),
						i.end_time.strftime("%H:%M"),
						i.status] for i in past_res]
		for data in past_data:
			data[4]="Used"     # Active rooms of the past, were occupied already
		past_res = list(zip(manager_links,past_data))	
			
		manager_links = [(i.manager_name,                 
						i.manager_email) for i in can_res]
		can_data = [[i.room_no,
						i.date.strftime("%Y-%m-%d"),
						i.start_time.strftime("%H:%M"),
						i.end_time.strftime("%H:%M"),
						i.status] for i in can_res]						
		can_res = list(zip(manager_links,can_data))		
		cont = dict()			
		cont['past'] = past_res
		cont['future'] = future_res
		cont['cancel'] = can_res
		cont['display'] = (bool(len(future_res)),bool(len(past_res)),bool(len(can_res)))
		return render(request,self.template,context=cont)
		
class DeleteReservation(View):
	
	def post(self,request,*args,**kwargs):
		room_no = request.POST['roomNo']
		start_time = datetime.time(datetime.strptime(request.POST['start'],"%H:%M"))
		date = datetime.date(datetime.strptime(request.POST['date'],"%Y-%m-%d"))
		
		this_room = Room.objects.filter(room_no=room_no)[0]
		this_slot = Slot.objects.filter(start_time=start_time)[0]
		this_reserve = Reservation.objects.filter(room=this_room,
													slot=this_slot,
													date=date)[0]	
		# NO TWO SLOTS CAN START AT THE SAME TIME
		# Simoultaneously setting status as Cancelled in Isolated Reservation Data 											
		this_iso_res = IsolatedResData.objects.filter(room_no=this_room.room_no,
													start_time=this_slot.start_time,
													date=date)[0]  
		
		this_iso_res.status = "Cancelled"
		this_iso_res.save()
		this_reserve.delete()
		messages.add_message(request,messages.SUCCESS,"Reservation Deleted")
		return HttpResponseRedirect(reverse('ManageReserve'))
	
	def get(self,request,*args,**kwargs):
		return HttpResponseRedirect(reverse('ManageReserve'))		           																						
		
                         
                          
        			
