from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),
    path('booking/new/', views.create_booking, name='create_booking'),
    path('booking/success/', views.booking_success, name='booking_success'),
    path('booking/update/<int:booking_id>/', views.update_booking, name='update_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('admin/pending-bookings/', views.pending_bookings, name='pending_bookings'),
    path('admin/approve-booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('admin/deny-booking/<int:booking_id>/', views.deny_booking, name='deny_booking'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('profile/', views.profile, name='profile'),
    path('info_and_faqs/', views.how_to_book, name='how_to_book'),
    path('document-upload/', views.document_upload, name='document_upload'),
]