from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)  # When it was create
    updated_on = models.DateTimeField(auto_now=True)  # When i was update

    class Meta:
        abstract = True


class Home(TimeStampedModel):
    """docstring for Home"""
    banner = models.ImageField(upload_to="home", null=True, blank=True)
    content = RichTextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Update HomePage')

class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="temtimonials")
    content = RichTextField()

    def __str__(self):
        return self.name

class Newsletter(TimeStampedModel):
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.email

class WhyChooseUs(TimeStampedModel):
    heading = models.CharField(max_length=255)
    content = RichTextField()
    image = models.ImageField(upload_to="why_us", null=True, blank=True)
    sort_by = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.heading


class ContactUsInfo(TimeStampedModel):
    """Admin/Support contact details"""
    email = models.EmailField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.email + " " + self.phone_number

class FAQ(TimeStampedModel):
    """docstring for Home"""
    question = models.CharField(max_length=255)
    answer = RichTextField()
    sr_no = models.IntegerField(default=0, verbose_name="Serial No.", help_text="For Sorting FAQ on page")

    def __str__(self):
        return self.question

class ServiceTerms(TimeStampedModel):
    """Add static content for Terms of service page"""
    content = RichTextField()

class PrivacyPolicy(TimeStampedModel):
    """Add static content for Privacy Policy page"""
    content = RichTextField()


class Contact(TimeStampedModel):
    """Store Contact form details"""
    full_name = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    phone = models.CharField(max_length=15)
    message = models.TextField()

    def __str__(self):
        return self.full_name
