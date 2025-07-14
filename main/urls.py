from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Announcement URLs
    path('', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('announcement/<int:pk>/', views.AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('announcement/create/', views.AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcement/<int:pk>/edit/', views.AnnouncementUpdateView.as_view(), name='announcement_update'),
    path('announcement/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='announcement_delete'),
    path('announcement/<int:pk>/archive/', views.archive_announcement, name='archive_announcement'),
    path('announcement/<int:pk>/unarchive/', views.unarchive_announcement, name='unarchive_announcement'),
    
    # Collection URLs
    path('collections/', views.CollectionListView.as_view(), name='collection_list'),
    path('collection/<int:pk>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path('collection/create/', views.CollectionCreateView.as_view(), name='collection_create'),
    path('collection/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='collection_delete'),
    
    # AJAX URLs for collection management
    path('ajax/add-to-collection/', views.add_to_collection, name='add_to_collection'),
    path('ajax/remove-from-collection/', views.remove_from_collection, name='remove_from_collection'),
    path('ajax/create-collection/', views.create_collection_ajax, name='create_collection_ajax'),
    
    # AJAX URLs for agency autocomplete
    path('ajax/agency-autocomplete/', views.agency_autocomplete, name='agency_autocomplete'),
    
    # AJAX URLs for complex autocomplete
    path('ajax/complex-autocomplete/', views.complex_autocomplete, name='complex_autocomplete'),
    
    # Account URL
    path('account/', views.AccountView.as_view(), name='account'),
    path('account/delete/', views.account_delete, name='account_delete'),
    path('ajax/upload-user-photo/', views.upload_user_photo, name='upload_user_photo'),
]

