from django.contrib import admin
from django.urls import path
from app01 import views

urlpatterns = [
    path('', views.passmng),
    path('login/', views.login),
    path('logout/', views.logout),
    path('console/passmng', views.passmng),
    path('console/redeemed', views.redeemed),
    path('console/usermanage', views.user_manage),
    path('console/add', views.add),
    path('edit/', views.edit),
    path('delete/', views.delete),
    path('mul_add/', views.mul_add),
    path('mul_del/', views.mul_del),
    path('user_mul_del/', views.user_mul_del),
    path('personal_delete/', views.personal_delete),
    path('etc/', views.etc),
    path('de_amount/', views.de_amount),
    path('searchPersonal/', views.search_personal),
    path('search_record/', views.search_record),
    path('search_recharge/', views.search_recharge),
    path('console/records/', views.records),
    path('search_record_by_date/', views.search_record_by_date),
    path('console/etc_history/', views.etc_history)
]
