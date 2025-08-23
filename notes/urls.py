from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'notes'

urlpatterns = [
    path('', views.notes, name='notes'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("group-notes", views.group_notes, name='group_notes'),
    path('notes/', views.notes, name='notes'),
    path('note_create/', views.note_create, name='note_create'),
    path('notes/delete/<int:note_id>/', views.note_delete, name='note_delete'),
    path('note<int:pk>/', views.note_detail, name='note_detail'),
    path('note/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('group/create/', views.create_group, name='create_group'),
]