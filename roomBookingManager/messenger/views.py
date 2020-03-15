from django.shortcuts import render
from django.views import View
from users.models import User, Customer, Manager, Admin
from .models import Message
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib import messages

def merge_sort(arr1,arr2):
	ret = list()
	ind1 = 0
	ind2 = 0
	while(ind1<len(arr1) and ind2<len(arr2)):  #dateTimeObjects in reverse order
		if(arr1[ind1][0]>=arr2[ind2][0]):
			ret.append(arr1[ind1])
			ind1 += 1
		else:
			ret.append(arr2[ind2])
			ind2 += 1
	if(ind1<len(arr1)):
		ret.extend(arr1[ind1:])
	else:
		ret.extend(arr2[ind2:])
	return ret

def last_occurrences(arr,this_user):
	ret = list()
	doneUsers = list()
	for message in arr:
		if (message.sender==this_user):
			check = message.receiver
		else:
			check = message.sender
		if check not in doneUsers:
			ret.append(message)
			doneUsers.append(check)
	return ret        
  
class OpenConversation(View):    
	""" Class based view to render the conversations pertaining to a 
	specific user upon his request
	"""	
		
	template = "messenger/Conversation.html"
	
	def post(self, request, *args, **kwargs):
		body = request.POST['toSend'].strip()
		if(len(body)>0):
			newMess = Message()
			newMess.sender = request.user
			newMess.receiver = list(User.objects.filter(id=request.POST['targetUser']))[0]
			newMess.body = request.POST['body']
			newMess.save()
		return HttpResponseRedirect(reverse('ViewMessages') )
		    
	def get(self, request, user_id, *args, **kwargs):
		try:
			this_user = request.user
			other_user = User.objects.get(id=user_id) #Refers to the User model object
			user_group = Group.objects.get(user=other_user).name
			if(user_group=="CustomerPrivilege"):
				other_inst = other_user.customer  #Refers to the Student objects
			elif(user_group=="ManagerPrivilege"):
				other_inst = other_user.manager
			elif(user_group=="AdminPrivilege"):
				other_inst = other_user.admin  
			sent_texts = list(Message.objects.filter(sender=this_user,receiver=other_user))
			recv_texts = list(Message.objects.filter(sender=other_user,receiver=this_user))

			for message in recv_texts:     #Mark all recvd_texts (since last read) as read   
				if not message.read:
					message.read = True
					message.save()
				else:
					break

			sent_texts = [(i.timestamp,i.body) for i in sent_texts]
			recv_texts = [(i.timestamp,i.body) for i in recv_texts]		                
			cont = dict()
			cont['RNum'] = user_id
			cont['other'] = other_user.name
			cont['sent'] = sent_texts
			cont['recv'] = recv_texts
			return render(request, self.template, context=cont)
		except User.DoesNotExists:
			messages.add_message(request, messages.ERROR, "User not found!")
			return HttpResponseRedirect(reverse('home'))
		    
        
class ViewMessages(View):
	""" Class based view to allow a user to see all messages he/she has sent or 
	recived in this web-application, and also search for a particular user by email ID
	"""
	
	template = "messenger/ViewMessages.html"
	
	def post(self, request, *args, **kwargs):
		search = request.POST['search'].strip()
		query = list(User.objects.filter(email=search))
		if(query):
			user_id = query[0].id
			return HttpResponseRedirect("/users/profile/"+str(user_id))
		else:
			messages.add_message(request, messages.ERROR, "Requested user could not be found!") 
			return HttpResponseRedirect(reverse("ViewMessages"))
	        
	def get(self, request, *args, **kwargs):		
		this_user = request.user
		Unread = list()
		Read = list()
		Pushoff = list()
		# Will have those messages that were sent by this user last and are unread on the other end
		# but this user must have read it already because he has sent he last message between them
		single_user_instances = last_occurrences(list(Message.objects.filter(sender=this_user)
									|Message.objects.filter(receiver=this_user)),this_user)
		# TO filter out only ONE occurrence of other user and list it						
		for message in single_user_instances: 							     
			if not message.read:    #UNREAD MESSAGES
				curr = [message.timestamp]
				if message.receiver==this_user:
					curr.append('from')   #W.R.T the current user
					if(message.sender==this_user):
						curr.append("me")               # Message from self
					else:
						curr.append(message.sender.name)
					curr.append(message.sender.id)
					Unread.append(curr) 
				else:
					curr.append('to')
					curr.append(message.receiver.name)   # For self messages, this is block is never entered
					curr.append(message.receiver.id)
					Pushoff.append(curr)       # Unread messages, if this_user is the sender, 
		            						   # Push them to read section as it has to be unread for other user
			else:
				curr = [message.timestamp]
				if message.receiver==this_user:
					curr.append('from')
					if(message.sender==this_user):
						curr.append("me")               # Message from self
					else:
						curr.append(message.sender.name)
					curr.append(message.sender.id)
				else:
					curr.append('to')
					curr.append(message.receiver.name)     # For self messages, this is block is never entered
					curr.append(message.receiver.id)
				Read.append(curr)
		Read = merge_sort(Read, Pushoff)      # Merging the The Pushed off and read messages, in sorted order

		cont = dict()
		cont['read'] = Read
		cont['display'] = (bool(Unread),bool(Read))
		cont['unread'] = Unread
		return render(request, self.template ,context=cont)
		

class CheckMessages(View):
	""" Class based view to check for any unread messages at the beginnning of a
	user session and redirect the user to the messages page
	"""

	template = 'messenger/CheckInbox.html'

	def get(self, request):
		this_user = request.user
		unread = (Message.objects.filter(receiver=this_user,read=False)).count()
		if(unread>0):
			cont = dict()
			cont['unread'] = unread
			messages.add_message(request, messages.SUCCESS, "You have "+str(unread)+" unread message(s). You are being redirected to the Messages page.")   
			return render(request, self.template, context=cont)
		else:
		    return HttpResponseRedirect(reverse("home"))
    
        

