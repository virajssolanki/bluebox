from django.db import models
from uuid import uuid4
import random
import string
from store import models as store_models
from settingadmin import models as setting_models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True) 
    updated_on = models.DateTimeField(auto_now=True)  

    class Meta:
        abstract = True


class UnavailableDates(models.Model):
    date = models.DateField()
    def __str__(self):
        return str(self.date)
    
    class Meta:
        verbose_name= _("Block Dates")


ORDER_STATUS = (
    ('pend', 'Pending'), ('prc', 'Processing'), ('cnf', 'Confirmed'),
    ('dlv', 'Delivered'), ('cncl', 'Cancelled'), ('com', 'Completed')
)


def generate_unique_code():
    length = 6

    while True:
        order_id = ''.join(random.choices(string.digits, k=length))
        if OrderDetail.objects.filter(order_id=order_id).count() == 0:
            break

    return order_id


class OrderDetail(TimeStampedModel):
    """All orders will be add here"""
    order_id = models.CharField(max_length=50, default=generate_unique_code)
    status = models.CharField(max_length=50, choices=ORDER_STATUS, default="pend", verbose_name="Order Status")
    delivery_date = models.DateField(blank=True, null=True)
    total = models.FloatField(null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)
    tax = models.FloatField(null=True, blank=True)
    extra_work = models.FloatField(null=True, blank=True)
    ordered_by = models.ForeignKey( 'order.PersonalDetail', verbose_name=('Customer'),
        on_delete=models.CASCADE, null=True, blank=True, related_name='orders',)
    used_voucher = models.ForeignKey( 'order.Discount', verbose_name=('used voucher'),
        on_delete=models.CASCADE, null=True, blank=True, related_name='orders',)
    
    class Meta:
        verbose_name = "Order"

    def __str__(self):
        return self.order_id


class CartItem(TimeStampedModel):
    cart_main_category = models.ForeignKey('store.Category', verbose_name=('Cart Product Category'),
        related_name='cart_main_product', on_delete=models.DO_NOTHING,)
    cart_sub_category = models.ForeignKey( 'store.SubCategory', verbose_name=('Cart Product Category'),
        related_name='cart_sub_product', on_delete=models.DO_NOTHING,)
    session = models.CharField(max_length=150, default='no session')
    rental = models.CharField(max_length=150, null=True, blank=True)
    rental_int = models.IntegerField(blank=True, null=True)
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, default=1)
    cart_price = models.FloatField(null=True, blank=True)
    inital_price = models.FloatField(default=1, null=True, blank=False)

    order = models.ForeignKey('order.OrderDetail', blank=True, null=True, related_name='cart_items' , on_delete=models.CASCADE)

    def __str__(self):
        return self.session + "--->" + self.product.title

    def save(self, *args, **kwargs):
        moving_price = { "1 Week": 1, "2 Week": 2, "3 Week": 3, "4 Week": 4, "5 Week": 5, "6 Week": 6, }
        query = store_models.PriceManagement.objects.filter(rental=self.rental).first()
        if query is not None:
            self.rental_int = moving_price[query.rental.period]
        if self.inital_price == None:
            self.inital_price = 1
        super(CartItem, self).save(*args, **kwargs)


class DeliveryAddress(TimeStampedModel):
    """Delivery Address item vise"""
    order = models.OneToOneField('order.OrderDetail', verbose_name=('Order Id'),
        on_delete=models.CASCADE, null=True, blank=True, related_name='delivery_adress',)
    session = models.CharField(max_length=150)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    apt_number = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    delivery_window_1 = models.ForeignKey('settingadmin.TimeSlots', verbose_name="Delivery Window 1", 
            on_delete=models.DO_NOTHING, related_name='adress', blank=True, null=True)
    delivery_window_2 = models.ForeignKey('settingadmin.TimeSlots', verbose_name="Delivery Window 2",
        on_delete=models.DO_NOTHING, related_name='adress2', blank=True, null=True)
    extra_work = models.ForeignKey( "settingadmin.ExtraWork", verbose_name="Extra Work",
        null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.delivery_date)


class PickupAddress(TimeStampedModel):
    """Pickup Address item vise"""
    order = models.OneToOneField('order.OrderDetail', verbose_name=('Order Id'),
        on_delete=models.CASCADE, null=True, blank=True, related_name='pickup_adress',)
    session = models.CharField(max_length=150)
    pickup_date = models.DateField(null=True, blank=True)
    pickup_address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    apt_number = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    pickup_window_1 = models.ForeignKey(
        'settingadmin.TimeSlots', verbose_name="Pickup Window 1",
        on_delete=models.DO_NOTHING, related_name='p_adress', blank=True, null=True)
    
    pickup_window_2 = models.ForeignKey('settingadmin.TimeSlots', verbose_name="Pickup Window 2",
        on_delete=models.DO_NOTHING, related_name='p_adress2', blank=True, null=True)

    extra_work = models.ForeignKey("settingadmin.ExtraWork", verbose_name="Extra Work",
        null=True, blank=True, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return str(self.pickup_date)


PAYMENT_STATUS = (
    ('pend', 'Pending'),
    ('prc', 'Processing'),
    ('cncl', 'Cancelled'),
    ('com', 'Completed')
)

class PaymentDetail(TimeStampedModel):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    order = models.OneToOneField("order.OrderDetail", on_delete=models.CASCADE, related_name='payment_details',)
    amount = models.FloatField()
    provider = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default="pend", verbose_name="Order Status")
    discount = models.CharField(max_length=50, blank=True, null=True)


COUPON_TYPES = (
    ('percentage', 'percentage'), 
    ('fix_amount', 'fix_amount'),
)

class Discount(TimeStampedModel):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=100)
    code = models.CharField(unique=True, max_length=350)
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES, null=True, blank=True)
    discount = models.IntegerField(blank=False, null=False,)
    min_order_value = models.FloatField(blank=False, null=False, )
    max_allowed_discount = models.FloatField(blank=False, null=False, )
    description = models.CharField(max_length=120, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title
    

class PersonalDetail(TimeStampedModel):
    """User personal details will be stored here"""
    session = models.CharField(max_length=150, default='no session')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email_address = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=15)
    secondary_phone_number = models.CharField(max_length=15, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    used_voucher = models.ManyToManyField(Discount, blank=True)
    hdyfu = models.ForeignKey("settingadmin.HDYFU", verbose_name="How Did You Find Us",
        on_delete=models.DO_NOTHING, null=True, blank=True,)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        verbose_name= _("Customers")