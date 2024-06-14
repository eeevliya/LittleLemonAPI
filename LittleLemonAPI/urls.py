from django.urls import path
from . import views

urlpatterns=[
    path('menu-items', views.MenuItemsView.as_view(), name = 'menu-items'),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<str:username>', views.ManagerRevokeView.as_view()),
    path('groups/delivery-crew/users',views.DeliveryCrewUsersView.as_view()),
    path('groups/delivery-crew/users/<str:username>', views.DeliveryCrewRevokeView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
    path('categories', views.CategoryView.as_view()),
]