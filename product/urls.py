from django.urls import path
from .views import *

app_name = 'product'

urlpatterns = [
    # Product Area CRUD urls
    path('area/create/', ProductAreaCreate.as_view(), name='create-product-area'),
    path('area/list/', ProductAreaList.as_view(), name='list-product-area'),
    path('area/<int:pk>/', ProductAreaView.as_view(), name='view-product-area'),
    path('area/teams/<int:pk>/', ProductAreaTeamsView.as_view(), name='team-product-area'),
    path('area/members/', ProductAreaMembersView.as_view(), name='product-area-members'),
    path('area/join/<int:pk>/', ProductAreaJoin.as_view(), name='product-area-join'),
    # Product CRUD urls
    path('create/', ProductCreate.as_view(), name='create-product'),
    path('list/', ProductList.as_view(), name='list-product'),
    path('<int:pk>/', ProductView.as_view(), name='view-product'),
    path('teams/<int:pk>/', ProductTeamsView.as_view(), name='team-product'),
    path('members/', ProductMembersView.as_view(), name='product-members'),
    path('join/<int:pk>/', ProductJoin.as_view(), name='product-join'),
    # Enterprise RU urls
    path('enterprise/', EnterpriseList.as_view(), name='enterprise-list'),
    path('enterprise/add/', EnterpriseProductsAdd.as_view(), name='enterprise-products-add'),
    # invites
    path('invite/', ProductsInvites.as_view(), name='product-invite'),
    # summary
    path('actionable/', Actionable.as_view(), name='actionable'),
    path('summary/', Summary.as_view(), name='summary'),

]