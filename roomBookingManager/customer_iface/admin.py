from django.contrib import admin
from .models import Reservation, IsolatedResData

admin.site.register(Reservation)
admin.site.register(IsolatedResData)
