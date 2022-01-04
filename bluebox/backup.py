from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from uuid import uuid4
import os
from django.utils.translation import gettext_lazy as _
from smart_selects.db_fields import ChainedForeignKey 

# Create your models here.


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)  # When it was create
    updated_on = models.DateTimeField(auto_now=True)  # When i was update

    class Meta:
        abstract = True


class TimeSlots(TimeStampedModel):
    """Deliver/Pickup Window Time Slots will be add here"""

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name = _('Delivery/Pickup TimeSlot')

    def __str__(self):
        return str(self.start_time) + "-" + str(self.end_time)


class Price(TimeStampedModel):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    slug = models.SlugField(unique=True, blank=True)
    price = models.FloatField()
    sort_by = models.IntegerField(default=0)

    def __str__(self):
        return self.price

class RentalPeriod(TimeStampedModel):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    period = models.CharField(max_length=100, verbose_name="Rental Period", help_text="Add period like 1 week, 2 week etc")
    slug = models.SlugField(unique=True, blank=True)

    is_active = models.BooleanField(default=True)
    sort_by = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.period)
        super(RentalPeriod, self).save(*args, **kwargs)

    def __str__(self):
        return self.period

class ExtraWork(TimeStampedModel):
    """Do you have stairs or an elevator?"""

    title = models.CharField(max_length=255)
    price = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = _("Do you have stairs or an elevator")

    def __str__(self):
        return self.title + " $" + str(self.price)


class Location(TimeStampedModel):
    """Add delivery Locations here"""

    title = models.CharField(max_length=100, verbose_name="Location", help_text="Add location i.e city,country etc")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class HDYFU(TimeStampedModel):
    """How Did you fide us options can be add/edit here"""
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('How Did You Find U')
        ordering = ['title']

    def __str__(self):
        return self.title


class Category(TimeStampedModel):
    """Table for main Category Home/Office"""
    title = models.CharField(max_length=20, unique=True, verbose_name="Category")
    slug = models.SlugField(unique=True, blank=True, help_text=("The name of the page as it will appear in URLs e.g http://domain.com/category/[my-slug]/"))

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    # Fetch related sub_categories
    def sub_categories(self):
        return [obj.title for obj in SubCategory.objects.filter(category=self)]


class SubCategory(TimeStampedModel):
    """Subcategories 1. Boxes Packages 2. Packing Supplies 3. Moving Supplies"""
    category = models.ForeignKey(
        'store.Category',
        verbose_name=('Category'),
        related_name='sub_category',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=100, verbose_name="Sub Category")
    slug = models.SlugField(unique=True, blank=True, help_text=("The name of the page as it will appear in URLs e.g http://domain.com/category/[my-slug]/"))

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.category.title + "-" + self.title)
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.category.title + "-->" + self.title


def upload_to(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    return "{category}/{product_category}/{filename}{extension}".format(
        category=slugify(instance.product_category.category.title),
        product_category=slugify(instance.product_category.title),
        filename=slugify(filename_base),
        extension=filename_ext.lower(),
    )


class BoxProducts(TimeStampedModel):
    """ Category vise Box Products will be stored here"""
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)

    title = models.CharField(max_length=100, verbose_name="Box Product Name")
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    price = models.FloatField()
    unit = models.CharField(max_length=64, help_text="Add product unit i.e $2 per lb,per week,per roll etc.")
    description = RichTextField()
    discount = models.ForeignKey("order.Discount", null=True, blank=True, on_delete=models.DO_NOTHING)

    product_category = models.ForeignKey(
        'store.Category',
        verbose_name=('Product Category'),
        related_name='box_products',
        on_delete=models.CASCADE,
    )

    rental = models.ForeignKey(
        "store.RentalPeriod",
        verbose_name=_("Rental Period"),
        on_delete=models.DO_NOTHING
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class PackingProducts(TimeStampedModel):
    """ Category vise Packing Products will be stored here"""
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)

    title = models.CharField(max_length=100, verbose_name="Packing Product Name")
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    price = models.FloatField()
    unit = models.CharField(max_length=64, help_text="Add product unit i.e $2 per lb,per week,per roll etc.")
    description = RichTextField()
    discount = models.ForeignKey("order.Discount", null=True, blank=True, on_delete=models.DO_NOTHING)

    product_category = models.ForeignKey(
        'store.Category',
        verbose_name=('Product Category'),
        related_name='packing_products',
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class MovingProducts(TimeStampedModel):
    """ Category vise Moving Products will be stored here"""
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)

    title = models.CharField(max_length=100, verbose_name="Moving Product Name")
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    price = models.FloatField()
    unit = models.CharField(max_length=64, help_text="Add product unit i.e $2 per lb,per week,per roll etc.")
    description = RichTextField()
    discount = models.ForeignKey("order.Discount", null=True, blank=True, on_delete=models.DO_NOTHING)

    product_category = models.ForeignKey(
        'store.Category',
        verbose_name=('Product Category'),
        related_name='moving_products',
        on_delete=models.CASCADE,
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Product(TimeStampedModel):
    """ Subcategory vise product will be stored here"""

    product_main_category = models.ForeignKey(
        'store.Category',
        verbose_name=('Main Category'),
        related_name='product',
        on_delete=models.CASCADE,
    )

    product_category = models.ForeignKey(
        'store.SubCategory',
        verbose_name=('Sub Category'),
        related_name='products',
        on_delete=models.CASCADE,
    )
    rental = models.ManyToManyField(
        "store.RentalPeriod",
        verbose_name=_("Rental Period")
    )
    discount = models.ForeignKey("order.Discount", null=True, blank=True, on_delete=models.DO_NOTHING)
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=100, verbose_name="Product Name")
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    price = models.FloatField()
    unit = models.CharField(max_length=64, help_text="Add product unit i.e $2 per lb,per week,per roll etc.")
    description = RichTextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

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
        verbose_name=_("Rental Period"),
        on_delete=models.DO_NOTHING
    )

    price = models.FloatField()

    def __str__(self):
        return u"{0}, {1}, {2}".format(self.product, self.rental, self.price)

# Quote

class Quote(TimeStampedModel):
    full_name = models.CharField(max_length=64, verbose_name="Full Name")
    email = models.EmailField(max_length=100, verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Phone Number")
    address = models.TextField(verbose_name="Where Do you live")
    delivery_date = models.DateField()

    def __str__(self):
        return self.full_name

# Newsletter


class Newsletter(TimeStampedModel):
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.email


class ZipCode(TimeStampedModel):
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.code
