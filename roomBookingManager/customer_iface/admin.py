from django.contrib import admin
from .models import Reservation, ReservedRoom

admin.site.register(Reservation)
admin.site.register(ReservedRoom)
