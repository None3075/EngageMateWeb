from django.urls import path
from . import views

urlpatterns = [
    path('', views.signin, name='home'),
    #path('signup/', views.signup, name='signup'),
    path('index', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('lectures/', views.lectures, name='lectures'),
    path('lectures/<int:id>/', views.selectLecture, name='selectLecture'),
    path('lectures/<int:id>/delete', views.deleteLecture, name='deleteLecture'),
    path('lectures/create/', views.createLecture, name='createLecture'),
    path('signout/', views.signout, name='signout'),
    path('signin/', views.signin, name='signin'),
    path('csvs/', views.csvs, name='csvs'),
    path('statistics/', views.statistics, name='statistics'),
    path('upload/', views.uploadCsv, name='uploadCsv'),
    path('hotsup/', views.hotsup, name='hotsup'),
    path('lectures/<int:id>/statistics/', views.statisticsLecture, name='statisticsLecture'),
    path('status/', views.status, name='status'),
]
