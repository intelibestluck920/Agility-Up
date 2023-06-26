from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path('team-list/', teamlist.as_view(), name='team-list'),
    path('team-detail/<int:pk>/', teamdetail.as_view(), name='team-detail'),
    path('team-create/', createteam.as_view(), name='team-create'),
    path('team-update/<int:pk>/', teamupdate.as_view(), name='team-update'),
    # path('task-delete/<str:pk>/', taskdelete, name='task-delete'),
    path('invite-member/', invitemember.as_view(), name='invite-member'),
    # path('invite-link/<int:pk>/', invitevialink.as_view(), name='invite-via-link'),
    path('join-team/<int:pk>/<str:slug>/', inviteduser.as_view(), name='invited-user'),
    path('team-members/<int:pk>/', get_team_members.as_view(), name='team-members'),
    path('create-sprint/', createsprint.as_view(), name='create-sprint'),
    path('sprint-info/<int:pk>/', get_team_sprints.as_view(), name='team-sprints'),
    path('submit-feedback/', feedback.as_view(), name='submit-feedback'),
    path('address-feedback/<int:pk>/', addressfeedback.as_view(), name='address-feedback'),
    path('get-analysis/<int:pk>/', get_analysis.as_view(), name='get-analysis'),
    # path('get-analysis/<int:pk>/<str:tag>/', get_analysis.as_view(), name='get-analysis'),
    path('get-current-sprint/<int:pk>/', get_current_sprint.as_view(), name='get-sprint'),
    path('get-history/', get_history.as_view(), name='get-history')

]