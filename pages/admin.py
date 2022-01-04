from django.contrib import admin
from pages import models


@admin.register(models.WhyChooseUs)
class WhyChooseUsAdmin(admin.ModelAdmin):
    model = models.WhyChooseUs
    list_display = ("heading", "content",)
    search_fields = ["heading", "content__icontains"]


# @admin.register(models.ContactUsInfo)
# class ContactUsInfoAdmin(admin.ModelAdmin):
#     model = models.ContactUsInfo
#     fields = ["email", "address", "phone_number"]
#     list_display = ("email", "address", "phone_number",)
#     search_fields = ["email", "address", "phone_number"]


@admin.register(models.Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("content",)
    search_fields = ["content"]
    # inlines = [WhyChooseUsInline, ContactUsInfoInline]


@admin.register(models.Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "occupation", "content", "image",)
    search_fields = ["name", "occupation"]


@admin.register(models.FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "answer",)
    search_fields = ["question", "answer"]


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "message", "created_on")
    search_fields = ["full_name", "email", "phone"]


# admin.site.register(models.ServiceTerms)
# admin.site.register(models.PrivacyPolicy)
