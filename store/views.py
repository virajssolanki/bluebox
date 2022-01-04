from django.shortcuts import render
from rest_framework import generics
# Create your views here.
from rest_framework.permissions import IsAdminUser
from store import models
from order import models as order_models
from settingadmin import models as setting_models
from store import serializers
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
import logging
logger = logging.getLogger(__name__)

class RentalListView(generics.ListAPIView):
    """Fetch all active rentals list"""
    queryset = models.RentalPeriod.objects.filter(is_active=True)
    serializer_class = serializers.RentalSerializer


class DeliveryWindowsView(generics.ListAPIView):
    """Fetch all Delivery Window slots """
    queryset = setting_models.TimeSlots.objects.all()
    serializer_class = serializers.TimeSlotsSerializer


class ExtraWorkListView(generics.ListAPIView):
    """Fetch ExtraWork options with price """
    queryset = setting_models.ExtraWork.objects.all()
    serializer_class = serializers.ExtraWorkSerializer

class UnavailableDattesListView(generics.ListAPIView):
    queryset = order_models.UnavailableDates.objects.all()
    serializer_class = serializers.UnavailableDatesSerializer

class BoxPackgeListView(generics.ListAPIView):
    """
    Box Packges products selected rental period vise!
    """
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        main_category = self.kwargs['main_category']
        sub_category = self.kwargs['sub_category']
        rental = self.kwargs['rental']
        queryset = models.Product.objects.filter(
            product_main_category__title__icontains=main_category,
            product_sub_category__title__icontains=sub_category,
        )
        return queryset.order_by('created_on')
#tedi di ni jem package id change kar vu jose hahhaaana aana mate to na jaroor pade
class ProductListView(generics.ListAPIView):
    """
    products categories vise!
    """
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        main_category = self.kwargs['main_category']
        sub_category = self.kwargs['sub_category']
        queryset = models.Product.objects.filter(
            product_main_category__title__icontains=main_category,
            product_sub_category__title__icontains=sub_category,
        )
        return queryset.order_by('created_on')

class LocationListView(generics.ListAPIView):
    """Get delivery locations"""
    queryset = setting_models.Location.objects.all()
    serializer_class = serializers.LocationSerializer

class NewsletterCreateView(generics.CreateAPIView):
    """Create Newsletter"""
    queryset = setting_models.Newsletter.objects.all()
    serializer_class = serializers.NewsletterSerializer

class QuoteCreateView(generics.CreateAPIView):
    """Save Free Quote Request"""
    queryset = setting_models.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer

class CheckZipCode(APIView):
    def post(self, reqest):
        response = {}
        for i in reqest.data:
            try:
                setting_models.ZipCode.objects.get(code=reqest.data[i])
            except setting_models.ZipCode.DoesNotExist:
                response['success'] = False
                response['message'] = 'Sorry! Your ' + str(i) + str(' is outside of our free service area. Contact us for potential availability and fees.')
                response['message_2'] = 'Sorry, that address isn\'t in our service area'
                return Response(response)
            response['success'] = True
            response['message_2'] = 'Services available in this area'
        return Response(response, status=status.HTTP_200_OK)

class CheckAdress(APIView):
    def post(self, reqest):
        response = {}
        for i in reqest.data:
            try:
                setting_models.ZipCode.objects.get(code=reqest.data[i])
            except setting_models.ZipCode.DoesNotExist:
                response['success'] = False
                response['message'] = 'Sorry, that address is not in our service area'
                return Response(response)
            response['success'] = True
        return Response(response, status=status.HTTP_200_OK)