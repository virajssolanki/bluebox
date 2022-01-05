from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from uuid import uuid4
import os
from django.utils.translation import gettext_lazy as _
# Create your models here.

class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)  # When it was create
    updated_on = models.DateTimeField(auto_now=True)  # When i was update

    class Meta:
        abstract = True


class RentalPeriod(TimeStampedModel):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    period = models.CharField(max_length=100, verbose_name="Rental Period", help_text="Add period like 1 week,2 week etc")
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_by = models.IntegerField(default=0)
    price = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.period)
        super(RentalPeriod, self).save(*args, **kwargs)

    def __str__(self):
        return self.period
    
    class Meta:
        verbose_name= _("Rental Period")
        verbose_name_plural = "RentalPeriod"  



class Category(TimeStampedModel):
    """Table for main Category Home/Office"""
    title = models.CharField(max_length=20, unique=True, verbose_name="Category")
    slug = models.SlugField(unique=True, blank=True, help_text=("The name of the page as it will appear in URLs e.g http://domain.com/category/[my-slug]/"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name= _("Category")
        verbose_name_plural = "Category"  



class SubCategory(TimeStampedModel):
    """Subcategories 1. Boxes Packages 2. Packing Supplies 3. Moving Supplies"""
    title = models.CharField(max_length=100, verbose_name="Sub Category", help_text=("Product SubCategory's title must contain Packing or Moving or Box word"))
    slug = models.SlugField(unique=True, blank=True, help_text=("The name of the page as it will appear in URLs e.g http://domain.com/category/[my-slug]/"))
    dynamic_pricing = models.BooleanField(default=False, help_text=("Uncheck if product type have multiple prices"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name= _("Sub Category")
        verbose_name_plural = "Sub Category"  


def upload_to(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    return "{product_main_category}/{product_sub_category}/{filename}{extension}".format(
        product_main_category=slugify(instance.product_main_category),
        product_sub_category=slugify(instance.product_sub_category),
        filename=slugify(filename_base),
        extension=filename_ext.lower(),
    )

class Product(TimeStampedModel):
    """ Subcategory vise product will be stored here"""
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)

    product_sub_category = models.ForeignKey(
        'store.SubCategory',
        verbose_name=('Sub Category'),
        related_name='products',
        on_delete=models.DO_NOTHING,
    )

    product_main_category = models.ManyToManyField(
        'store.Category',
        verbose_name=('Category'),
        related_name='products',
    )

    discount = models.ForeignKey("order.Discount", null=True, blank=True, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100, verbose_name="Product Name")
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=64,verbose_name="Price description", help_text="Add product unit i.e $2 per lb,per week,per roll etc.")
    description = RichTextField()
    description_image = models.ImageField(upload_to=upload_to, null=True, blank=True)

    total_boxes = models.IntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    description_image = models.ImageField(upload_to=upload_to, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product"    


class PriceManagement(TimeStampedModel):
    """ Product, week vise prices will be stored here"""
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    product = models.ForeignKey(
        'store.Product',
        verbose_name=('Product'),
        related_name='prices',
        on_delete=models.CASCADE,
    )
    rental = models.ForeignKey(
        "store.RentalPeriod",
        verbose_name=_("period"),
        on_delete=models.DO_NOTHING
    )
    price = models.FloatField()

    def __str__(self):
        return self.product.title + "  -  " + self.rental.period + "  -  " + str(self.price)

    class Meta:
        verbose_name = "Price Management"
        verbose_name_plural = "Price Management"  


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