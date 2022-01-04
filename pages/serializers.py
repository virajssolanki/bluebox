from rest_framework import serializers
from pages import models
from settingadmin import models as adminmodels

from settingadmin import models as setting_models
from django.core.exceptions import MultipleObjectsReturned

class WhyChooseUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WhyChooseUs
        fields = ['heading', 'content','image','sort_by']

class HDFYUSerializer(serializers.ModelSerializer):
    class Meta:
        model = adminmodels.HDYFU
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Testimonial
        fields = ['name', 'occupation', 'image', 'content']

class ContactUsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactUsInfo
        fields = ['email', 'address', 'phone_number']

class HomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Home
        fields = ['banner', 'content']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FAQ
        fields = ['id', 'question', 'answer']

class ServiceTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceTerms
        fields = ['content']

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PrivacyPolicy
        fields = ['content']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = "__all__"