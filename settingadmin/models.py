from django.db import models
from django.utils.translation import gettext_lazy as _

class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)  # When it was create
    updated_on = models.DateTimeField(auto_now=True)  # When i was update

    class Meta:
        abstract = True

class ExtraWork(TimeStampedModel):
    """Do you have stairs or an elevator?"""
    title = models.CharField(max_length=255)
    price = models.FloatField(default=0, null=False, blank=False)

    class Meta:
        verbose_name = _("Stairs or an Elevator")
        app_label = 'settingadmin'

    def __str__(self):
        return self.title + " $" + str(self.price)


class Location(TimeStampedModel):
    """Add delivery Locations here"""
    title = models.CharField(max_length=100, verbose_name="Location", help_text="Add location i.e city,country etc")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Location"  


class OrderIdPrefix(TimeStampedModel):
    prefix = models.CharField(max_length=20, help_text="all order id will start with prefix")

    def __str__(self):
        return self.prefix

    class Meta:
        verbose_name = "OrderId Prefix"
        verbose_name_plural = "OrderId Prefix"  


class TimeSlots(TimeStampedModel):
    """Deliver/Pickup Window Time Slots will be add here"""
    start_time = models.CharField(max_length=40, blank=True, null=True)
    end_time =  models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        verbose_name = _('Delivery/Pickup TimeSlot')
        
    def __str__(self):
        return str(self.start_time) + "-" + str(self.end_time)


class HDYFU(TimeStampedModel):
    """How Did you fide us options can be add/edit here"""
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('How Did You Find U')
        ordering = ['title']

    def __str__(self):
        return self.title


class ZipCode(TimeStampedModel):
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "ZipCode"
        verbose_name_plural = "ZipCode"  


class Newsletter(TimeStampedModel):
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletter"  


class Quote(TimeStampedModel):
    full_name = models.CharField(max_length=64, verbose_name="Full Name")
    email = models.EmailField(max_length=100, verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Phone Number")
    address = models.TextField(verbose_name="Where Do you live")
    delivery_date = models.DateField()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Quote"
        verbose_name_plural = "Quote"  


class Tax(TimeStampedModel):
    tax = models.FloatField(blank=False, null=False,
                                verbose_name = 'tax in %', 
                                help_text = 'enter tax % for packing supplies')

    def __str__(self):
        return str(self.tax)

    class Meta:
        verbose_name = "Tax"
        verbose_name_plural = "Tax"  