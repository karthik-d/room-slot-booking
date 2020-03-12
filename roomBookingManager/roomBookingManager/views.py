from django.shortcuts import render
from django.views import View

class MainLanding(View):
	template = 'users/base.html'	
	
	def get(self, request):
		return render(request, self.template)
