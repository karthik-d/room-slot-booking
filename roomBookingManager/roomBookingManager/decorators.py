from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from functools import wraps

def group_required(*group_names, redirect_view=None):
	""" Custom Decorator to make sure the requesting user is a part of
	one of the required groups
	"""
	
	def actual_decorator(function):
		@wraps(function)
		def wrapper(request, *args, **kwargs):
			if(bool(request.user.groups.filter(name__in=group_names))):
				return function(request, *args, **kwargs)
			else:
				if(not redirect_view):
					messages.add_message(request, messages.ERROR, "You have been logged out")	
					return HttpResponseRedirect(reverse('Logout'))
				messages.add_message(request, messages.ERROR, "Access Denied. Login with necessary authorisation")	
				return HttpResponseRedirect(reverse(redirect_view))
		return wrapper
	return actual_decorator	
	
	
def anonymous_required(redirect_view=None):
	""" Customer Decorator to check whether the requesting user is not logged in 
	at present
	"""
	
	def actual_decorator(function):
		@wraps(function)
		def wrapper(request, *args, **kwargs):
			if(request.user.is_anonymous):
				return function(request, *args, **kwargs)
			else:
				if(not redirect_view):
					messages.add_message(request, messages.ERROR, "You have been logged out")	
					return HttpResponseRedirect(reverse('Logout'))
				messages.add_message(request, messages.ERROR, "Please Logout First")
				return HttpResponseRedirect(reverse(redirect_view))
		return wrapper
	return actual_decorator	
			
		
'''def class_decorator(decorator):
    def inner(cls):
        orig_dispatch = cls.dispatch
        @method_decorator(decorator)
        def new_dispatch(self, request, *args, **kwargs):
            return orig_dispatch(self, request, *args, **kwargs)
        cls.dispatch = new_dispatch
        return cls
    return inner  ''' 

