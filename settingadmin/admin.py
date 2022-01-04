from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin


# Register your models here.
admin.site.register(models.HDYFU)
admin.site.register(models.Tax)
admin.site.register(models.OrderIdPrefix)
@admin.register(models.Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "address", "delivery_date", "created_on",)
    search_fields = ["full_name", "email", "phone", "address", "delivery_date", "created_on"]


@admin.register(models.Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "created_on",)
    search_fields = ["email", "created_on"]


@admin.register(models.ZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ("code",)
    search_fields = ["code"]

@admin.register(models.ExtraWork)
class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ("title",)

@admin.register(models.Location)
class RentalPeriodAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ["title"]

@admin.register(models.TimeSlots)
class RentalPeriodAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ("start_time","end_time")
