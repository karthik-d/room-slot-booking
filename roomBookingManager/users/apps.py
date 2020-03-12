from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UsersConfig(AppConfig):
    name = 'users'
    
    def ready(self):
    	from users.configs.signals import create_groups, create_base_admin   #Can be imported only when "ready"
    	post_migrate.connect(create_groups,sender=self)   # To listen for a post migrate signal and invoke create_groups
    	post_migrate.connect(create_base_admin,sender=self)
