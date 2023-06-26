from django.contrib import admin
from .models import *


# Register your models here.

class ProductAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_area_creator', 'product_area_lead')
    search_fields = ('name', 'product_area_creator', 'product_area_lead')


class ProductAreaTeamsAdmin(admin.ModelAdmin):
    list_display = ('id', 'Team', 'Product_Area')
    search_fields = ('Team', 'Product_Area')


class ProductAreaMembersAdmin(admin.ModelAdmin):
    list_display = ('id', 'User', 'Product_Area')
    search_fields = ('User', 'Product_Area')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_creator', 'product_lead')
    search_fields = ('name', 'product_creator', 'product_lead')


class ProductTeamsAdmin(admin.ModelAdmin):
    list_display = ('id', 'Product_Area', 'Product')


class ProductMembersAdmin(admin.ModelAdmin):
    list_display = ('id', 'User', 'Product')


class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner',)


class EnterpriseProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'Enterprise', 'Product')


admin.site.register(ProductArea, ProductAreaAdmin)
admin.site.register(ProductAreaTeams, ProductAreaTeamsAdmin)
admin.site.register(ProductAreaMembers, ProductAreaMembersAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductTeams, ProductTeamsAdmin)
admin.site.register(ProductMembers, ProductMembersAdmin)
admin.site.register(Enterprise, EnterpriseAdmin)
admin.site.register(EnterpriseProducts, EnterpriseProductsAdmin)
