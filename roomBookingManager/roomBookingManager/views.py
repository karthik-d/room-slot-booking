from django.shortcuts import render
from django.views import View

class MainLanding(View):
	template = 'users/Home.html'	
	
	def get(self, request):
		return render(request, self.template)
