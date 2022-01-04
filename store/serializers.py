from rest_framework import serializers
from store import models
from order import models as order_models
from settingadmin import models as setting_models


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RentalPeriod
        fields = ["id", 'period', 'price', 'sort_by']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = setting_models.Location
        fields = ['title']


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    period = serializers.SerializerMethodField()
    period_id = serializers.SerializerMethodField()

    def get_price(self, product_obj):
        if product_obj.product_sub_category.dynamic_pricing == False:
            return product_obj.price
        else:
            query = models.PriceManagement.objects.filter(product=product_obj).filter(rental__period__icontains=self.context['request'].path.split('/')[-2]).all()
            for i in query:
                return i.price

    def get_quantity(self, product_obj):
        return 1 

    def get_period(self, product_obj):
        query = models.RentalPeriod.objects.filter(period__icontains=self.context['request'].path.split('/')[-2]).all()
        for i in query:
            return i.period

    def get_period_id(self, product_obj):
        query = models.RentalPeriod.objects.filter(period__icontains=self.context['request'].path.split('/')[-2]).all()
        for i in query:
            return i.id

    class Meta:
        model = models.Product
        fields = "__all__"

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['rental'] = RentalSerializer(instance.rental).data
    #     return response


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = setting_models.Quote
        fields = "__all__"


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = setting_models.Newsletter
        fields = "__all__"

class TimeSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = setting_models.TimeSlots
        fields = "__all__"

class ExtraWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = setting_models.ExtraWork
        fields = "__all__"

class UnavailableDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_models.UnavailableDates
        fields = '__all__'