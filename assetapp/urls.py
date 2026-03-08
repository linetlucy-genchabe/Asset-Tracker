from django.urls import path
from . import views

urlpatterns = [
    path('',                             views.dashboard,     name='dashboard'),
    path('dashboard/',                   views.dashboard,     name='dashboard'),
    path('devices/',                     views.device_list,   name='device_list'),
    path('devices/add/',                 views.device_add,    name='device_add'),
    path('devices/<int:pk>/',            views.device_detail, name='device_detail'),
    path('devices/<int:pk>/edit/',       views.device_edit,   name='device_edit'),
    path('devices/<int:pk>/status/',     views.device_status, name='device_status'),
    path('profile/',                     views.profile,       name='profile'),
    path('chps/',                          views.chp_list,      name='chp_list'),
    path('chps/add/',                      views.chp_add,       name='chp_add'),
    path('chps/<int:pk>/edit/',            views.chp_edit,      name='chp_edit'),
]