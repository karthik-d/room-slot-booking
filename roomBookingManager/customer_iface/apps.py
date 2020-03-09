from django.apps import AppConfig
from django.db.models.signals import pre_delete, post_save, pre_save

class CustomerIfaceConfig(AppConfig):
	name = 'customer_iface'
    
	def ready(self):
		from .configs.signals import set_iso_res_cancelled, change_iso_slot, create_iso_res, delete_iso_res
		from customer_iface.models import Reservation
		from manager_iface.models import Slot
		from users.models import Customer
		pre_delete.connect(set_iso_res_cancelled, sender=Reservation)
		pre_delete.connect(delete_iso_res, sender=Customer)
		pre_save.connect(create_iso_res, sender=Reservation)
		post_save.connect(change_iso_slot, sender=Slot)
