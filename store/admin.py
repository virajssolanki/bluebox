from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django import forms #CheckboxSelectMultiple
from django.forms import CheckboxSelectMultiple

from store import models
from django.contrib.auth.models import Group

admin.site.unregister(Group)
"""Inline Models"""

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["title", "slug"]
    fields = ['title', "slug"]


@admin.register(models.SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    search_fields = ["title", "slug", "dynamic_pricing"]
    fields = ['title', "slug", "dynamic_pricing"]


@admin.register(models.RentalPeriod)
class RentalPeriodAdmin(admin.ModelAdmin):
    list_display = ("id", "period",)
    search_fields = ["period"]


class PriceInlineFormSet(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PriceInlineFormSet, self).__init__(*args, **kwargs)
        rental = []
        for i in models.RentalPeriod.objects.all():
            rental.append({'rental': i},)
        self.initial = rental


class PriceInline(admin.TabularInline):
    model = models.PriceManagement
    extra = len(models.RentalPeriod.objects.all())
    max_num = len(models.RentalPeriod.objects.all())
    formset = PriceInlineFormSet     


class ItemAdmin(admin.ModelAdmin):    
    list_display = ("title", "product_sub_category")
    search_fields = ['title']


class Box_Products(models.Product):
    class Meta:
        proxy = True
        verbose_name = ("Box Product")
        verbose_name_plural = "Box Product"


class BoxProductsAdmin(ItemAdmin):
    fields = ['product_main_category','product_sub_category', 'title', 'total_boxes', 'image', 'description', 'description_image']
    inlines = [PriceInline]

    def get_queryset(self, request):
        return self.model.objects.filter(product_sub_category__title__icontains='Box')

    def get_form(self, request, obj=None, **kwargs):
        form = super(BoxProductsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['product_sub_category'].initial = models.SubCategory.objects.filter(title__icontains='Box').first()
        form.base_fields['product_sub_category'].widget = forms.HiddenInput()
        return form


class Moving_Products(models.Product):
    class Meta:
        proxy = True
        verbose_name = ("Moving Supply")
        verbose_name_plural = "Moving Supply"



class MovingProductsAdmin(ItemAdmin):
    fields = ['product_main_category','product_sub_category', 'title', 'subtitle', 'price', 'unit', 'image', 'description']

    def get_queryset(self, request):
        return self.model.objects.filter(product_sub_category__title__icontains='Moving')

    def get_form(self, request, obj=None, **kwargs):
        form = super(MovingProductsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['product_sub_category'].initial = models.SubCategory.objects.filter(title__icontains='Moving').first()
        form.base_fields['product_sub_category'].widget = forms.HiddenInput()
        return form

class Packing_Products(models.Product):
    class Meta:
        proxy = True
        verbose_name = ("Packing Supply")
        verbose_name_plural = "Packing Supply"


class PackingProductsAdmin(ItemAdmin):
    fields = ['product_main_category','product_sub_category', 'title', 'price', 'unit', 'subtitle', 'image', 'description']

    def get_queryset(self, request):
        return self.model.objects.filter(product_sub_category__title__icontains='Packing')

    def get_form(self, request, obj=None, **kwargs):
        form = super(PackingProductsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['product_sub_category'].initial = models.SubCategory.objects.filter(title__icontains='Packing').first()
        form.base_fields['product_sub_category'].widget = forms.HiddenInput()
        return form

admin.site.register(Box_Products, BoxProductsAdmin)
admin.site.register(Moving_Products, MovingProductsAdmin)
admin.site.register(Packing_Products, PackingProductsAdmin)
