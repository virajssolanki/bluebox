from django.contrib import admin
from order import models
from django import forms 
from django.db import models as dbmodels
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import DateInput, DateTimeInput
# from bluebox.widgets import AvailableDateWidget
import json


from datetime import date
from django import forms 

class CustomDatePicker(forms.DateInput):
    def __init__(self, attrs={}, format=None):
        attrs.update(
            {
                'class': 'form-control',
                'type': 'text',
            }
        )
        self.format = format
        super().__init__(attrs, format=self.format)

class AvailableDateWidget(CustomDatePicker):
    def __init__(self, attrs={}, format=None):
        attrs.update({'autocomplete':'Off'})
        super().__init__(attrs, format=format)

    class Media:
        css = {
            'all': ('http://code.jquery.com/ui/1.9.2/themes/smoothness/jquery-ui.css',),
        }
        js = (
            "http://code.jquery.com/jquery-1.8.3.min.js",
            "http://code.jquery.com/ui/1.9.2/jquery-ui.js",
            "js/admin/custom.js",
        )
    
#     def get_context(self, name, value, attrs):
#         datetimepicker_id = 'datetimepicker_{name}'.format(name=name)
#         if attrs is None:
#             attrs = dict()
#         attrs['data-target'] = '#{id}'.format(id=datetimepicker_id)
#         attrs['class'] = 'form-control datetimepicker-input'
#         context = super().get_context(name, value, attrs)
#         context['widget']['datetimepicker_id'] = datetimepicker_id
#         return context

@admin.register(models.UnavailableDates)
class UnavailableDatesAdmin(admin.ModelAdmin):
    list_display = ("date",)
    search_fields = ["date"]
    
    formfield_overrides = {
        dbmodels.DateField: {'widget': AvailableDateWidget},
    }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        list = [1,2,3,'String1']
        json_list = json.dumps(list)
        print(json_list)
        extra_context['list'] = json_list
        print(extra_context)
        return super(UnavailableDatesAdmin, self).changelist_view(request, extra_context=extra_context)
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(UnavailableDatesAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['date'].widget = CustomDateField()
    #     return form

    # class Media:
    #     css = {
    #         'all': ('css/checkbox-override.css',),
    #     }

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(ItemAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['product_main_category'].widget = CheckboxSelectMultiple()
    #     return form

    # def formfield_for_manytomany(self, db_field, request=None, **kwargs):
    #     if db_field.name == 'product_main_category':
    #         print('im inti')
    #         kwargs['widget'] = forms.widgets.SelectMultiple()
    #         kwargs['help_text'] = ''
    #     else:
    #         print('not even in')
    #     return db_field.formfield(**kwargs)

class CartItemsInline(admin.TabularInline):
    model = models.CartItem
    can_delete = False
    extra = 0
    fields = ["product", "quantity", "cart_price", "order"]
    readonly_fields = fields


class DeliveryAddressInline(admin.TabularInline):
    model = models.DeliveryAddress
    fields = ["delivery_date", "delivery_address", "apt_number", "description"]
    can_delete = False
    extra = 0
    readonly_fields = fields

class PickupAddressInline(admin.TabularInline):
    model = models.PickupAddress
    fields = ["pickup_date", "pickup_address", "apt_number", "description"]
    can_delete = False
    extra = 0
    readonly_fields = fields

class PersonalDetailInline(admin.TabularInline):
    model = models.PersonalDetail
    extra = 0
    fields = ["first_name", "last_name", "email_address", "phone_number", "company_name", "hdyfu",]


class PaymentDetailInline(admin.TabularInline):
    model = models.PaymentDetail
    fields = ["amount", "provider", "status"]
    can_delete = False
    extra = 0
    readonly_fields = fields

@admin.register(models.OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ("order_id", "ordered_by", "total", "status", "delivery_date")
    search_fields = ["order_id", "delivery_date"]
    can_delete = False
    inlines = [CartItemsInline, DeliveryAddressInline, PickupAddressInline, PaymentDetailInline,]

@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("product", "session", "quantity",)
    search_fields = ["product", "session", "quantity"]


class DiscountAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "expiry_date")


# class FixDiscountAdmin(DiscountAdmin):
#     fields = [
#         "title", "code", "fix_discount_amount", "description", "min_order_value", 
#         "max_allowed_discount",  "expiry_date", "coupon_type"
#     ]

#     def get_queryset(self, request):
#         return self.model.objects.filter(coupon_type="fix_amount").all()
    
#     def get_form(self, request, obj, **kwargs):
#         form = super(FixDiscountAdmin, self).get_form(request, obj, **kwargs)
#         form.base_fields['coupon_type'].initial = "fix_amount"
#         form.base_fields['coupon_type'].widget = forms.HiddenInput()
#         return form 

# class PercentageDiscountAdmin(DiscountAdmin):
#     fields = [
#         "title", "code", "discount_percentage", "description", "min_order_value", 
#         "max_allowed_discount",  "expiry_date", "coupon_type"
#     ]

#     def get_queryset(self, request):
#         return self.model.objects.filter(coupon_type="percentage").all()
    
#     def get_form(self, request, obj, **kwargs):
#         form = super(PercentageDiscountAdmin, self).get_form(request, obj, **kwargs)
#         form.base_fields['coupon_type'].initial = "percentage"
#         form.base_fields['coupon_type'].widget = forms.HiddenInput()
#         return form

admin.site.register(models.Discount)
admin.site.register(models.DeliveryAddress)
admin.site.register(models.PickupAddress)
admin.site.register(models.PersonalDetail)