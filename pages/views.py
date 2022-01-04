from django.shortcuts import render
from rest_framework import generics
# Create your views here.
from rest_framework.permissions import IsAdminUser
from pages import models
from settingadmin import models as adminmodels
from pages import serializers
from rest_framework import viewsets, generics

class HomeListView(generics.ListAPIView):
    queryset = models.Home.objects.all()
    serializer_class = serializers.HomeSerializer

class FAQListView(generics.ListAPIView):
    queryset = models.FAQ.objects.all().order_by('-sr_no')
    serializer_class = serializers.FAQSerializer

class ServicesListView(generics.ListAPIView):
    queryset = models.ServiceTerms.objects.all()
    serializer_class = serializers.ServiceTermsSerializer

class PolicyListView(generics.ListAPIView):
    queryset = models.PrivacyPolicy.objects.all()
    serializer_class = serializers.PrivacyPolicySerializer


class ContactListView(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer

class TestimonialListView(generics.ListAPIView):
    queryset = models.Testimonial.objects.all()
    serializer_class = serializers.TestimonialSerializer

class WhyChooseUsListView(generics.ListAPIView):
    queryset = models.WhyChooseUs.objects.all().order_by('sort_by')
    serializer_class = serializers.WhyChooseUsSerializer

class HDYFUListView(viewsets.ModelViewSet):
    queryset = adminmodels.HDYFU.objects.all()
    serializer_class = serializers.HDFYUSerializer

class ContactUsInfoListView(viewsets.ModelViewSet):
    queryset = models.ContactUsInfo.objects.all()
    serializer_class = serializers.ContactUsInfoSerializer