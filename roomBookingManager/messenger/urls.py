from django.urls import path
from . import views

urlpatterns = [path('view-messages', views.ViewMessages.as_view(), name="ViewMessages"),
               path('open-conv/<int:user_id>', views.OpenConversation.as_view() ,name="OpenConversation"),
               path('check-inbox', views.CheckMessages.as_view(), name="CheckMessages")
]
