from django.urls import path
from . import views

urlpatterns=[
    path('menu-items', views.MenuItemsView.as_view(), name = 'menu-items'),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.ManagerUsersView.as_view()),
]