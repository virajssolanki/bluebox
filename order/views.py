from django.shortcuts import render
from rest_framework.decorators import api_view, action
from order import models as order_models
from store import models as store_models
from settingadmin import models as admin_models
from order import serializers
from rest_framework.views import APIView
from datetime import datetime, date, timedelta
from django.conf import settings
from bluebox.email import send_email
from django.forms.models import model_to_dict

# Create your views here.
import stripe
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from rest_framework.permissions import AllowAny

stripe.api_key = "sk_test_51JdOT3JfjdazBivChggHWPxrICmfgFfD4I9HoWRXGaC3SMymfGYkJQjiPy5I656RQ3xlArJNjBtq8HuTPNrJmQr600Uy6uWHWa"


def _send_order_email(order):
    packing_items = order_models.CartItem.objects.filter(
                        order=order, cart_sub_category__title__icontains='Packing').all()
    moving_items = order_models.CartItem.objects.filter(
                        order=order, cart_sub_category__title__icontains='Moving').all()
    package_items = order_models.CartItem.objects.filter(
                        order=order, cart_sub_category__title__icontains='Box').all()
    context = {}
    packing_supplies = []
    for i in packing_items:
        dict = {}
        dict['cart_price'] = i.cart_price
        dict['title'] = i.product.title
        packing_supplies.append(dict)
    context['packing_supplies'] = packing_supplies

    moving_supplies = []
    for i in moving_items:
        dict = {}
        dict['cart_price'] = i.cart_price
        dict['title'] = i.product.title
        moving_supplies.append(dict)
    context['moving_supplies'] = moving_supplies

    packages = []
    for i in package_items:
        dict = {}
        dict['cart_price'] = i.cart_price
        dict['title'] = i.product.title
        dict['rental'] = i.rental
        packages.append(dict)
    context['packages'] = packages
    context['package_type'] = package_items[0].cart_main_category.title
    query = store_models.PriceManagement.objects.filter(rental=package_items[0].rental).first()
    if query is not None:
        context['rental'] = query.rental.period
    
    context['order'] = model_to_dict(order)        
    context['customer'] = model_to_dict(order.ordered_by)
    context['pickup_address'] = model_to_dict(order.pickup_adress)
    context['delivery_address'] = model_to_dict(order.delivery_adress)
    context['d_window'] = model_to_dict(order.delivery_adress.delivery_window_1)
    context['d_window2'] = model_to_dict(order.delivery_adress.delivery_window_2)

    context['p_window'] = model_to_dict(order.pickup_adress.pickup_window_1)
    context['p_window2'] = model_to_dict(order.pickup_adress.pickup_window_2)
    
    send_email(settings.ADMINS, 'New order received', 'order-confirmation-admin.html', context)
    send_email([order.ordered_by.email_address,], 'Order Placed', 'order-confirmation-customer.html', context)      
    return True


@api_view(['POST'])
def test_payment(request):
    test_payment_intent = stripe.PaymentIntent.create(
        amount=100, currency='pln',
        payment_method_types=['card'],
        receipt_email='test@example.com')
    print("test_payment_intent", test_payment_intent)
    return Response(status=status.HTTP_200_OK, data=test_payment_intent)


@api_view(['POST'])
def save_stripe_info(request):
    order_id = request.data["session"]
    amount = request.data["amount"]
    discount = request.data["discount"]

    order = order_models.OrderDetail.objects.filter(order_id=order_id).first()
    payment_detail = order_models.PaymentDetail.objects.create(order=order, amount=amount, discount=discount, status='prc')
    payment_detail.save()

    # try:
    payment = request.data["payment"]
    if order is None:
        return Response({'msg': 'No order found'}, status=status.HTTP_200_OK)
        
    name = payment['billing_details']
    email = payment['billing_details']['email']
    customer_data = stripe.Customer.list(email=payment['billing_details']['email']).data
    if len(customer_data) == 0:
        customer = stripe.Customer.create(email=email)
    else:
        customer = customer_data[0]

    stripe.PaymentIntent.create(
        customer=customer,
        payment_method = payment['id'],
        currency = 'usd', 
        amount = int(amount*100),
        confirm = True,) 

    payment_detail.status = 'com'
    payment_detail.save()
    _send_order_email(order)

    return Response(status=status.HTTP_200_OK,
                        data={
                            "success": True,
                            'message': 'Success',
                        })
    # except Exception as error:
    #     print(error)
    #     return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                     data={
    #                         "success": False,
    #                         'message': 'Payment failed!',
    #                         'error': str(error)
    #                     })

class OrderListView(generics.ListAPIView):
    serializer_class = serializers.OrderSerializer
    def get_queryset(self):
        order_id = self.request.query_params.get('order_id')
        queryset = order_models.OrderDetail.objects.filter(
            order_id=order_id,
        ).order_by('created_on')
        return queryset


class CartListView(generics.ListAPIView):
    serializer_class = serializers.CartSerializer

    def get_queryset(self):
        session = self.kwargs['session']
        cart_sub_category = self.kwargs['cart_sub_category']
        
        queryset = order_models.CartItem.objects.filter(
            session=session,
            cart_sub_category__id=cart_sub_category,
        ).order_by('created_on')
        return queryset


class SessionCartListView(generics.ListAPIView):
    serializer_class = serializers.CartSerializer

    def get_queryset(self):
        session = self.kwargs['session']       
        queryset = order_models.CartItem.objects.filter(
            session=session,
        ).order_by('created_on')
        return queryset

def _tax_cart_total(session):
    packing_cart_total = 0
    total_tax = 0
    tax = 0
    packing_items = order_models.CartItem.objects.filter(
                                            session=session,
                                            cart_sub_category__title__icontains='Packing').all()
    try:
        tax = admin_models.Tax.objects.first().tax
    except:
        pass
    if len(packing_items) > 0: 
        for i in packing_items:
            packing_cart_total += i.cart_price*i.quantity
        total_tax = round(packing_cart_total*tax/100, 2)
        # total_tax = packing_cart_total*tax/100
    return total_tax


def _session_cart_total(session):
    session_cart_total = 0
    extra_cost = 0
    cart_items = order_models.CartItem.objects.filter(session=session).all()
    packing_items = order_models.CartItem.objects.filter(
                                            session=session,
                                            cart_sub_category__title__icontains='Packing').all()
    delivery_extra = order_models.DeliveryAddress.objects.filter(session=session).first()
    pickup_extra = order_models.PickupAddress.objects.filter(session=session).first()
    for i in [delivery_extra, pickup_extra]:
        try:
            session_cart_total = session_cart_total + i.extra_work.price
            extra_cost = extra_cost + i.extra_work.price
        except:
            pass
    if len(cart_items) > 0: 
        for i in cart_items:
            session_cart_total += i.cart_price*i.quantity
    tax = _tax_cart_total(session)
    session_cart_total = session_cart_total + tax
    return {'session_cart_total': session_cart_total, 'extra_cost': extra_cost, 'tax':tax}


def _calculate_discount(code, session_cart_total):
    discounted_session_total = 0
    if session_cart_total < code.min_order_value:
        return {'success': 'false','msg': 'Minimum order value is {0}'.format(code.min_order_value)}
    if code.coupon_type == "percentage":
        discount = session_cart_total * code.discount / 100
        discounted_session_total = session_cart_total - discount
    elif code.coupon_type == "fix_amount":
        discount = code.discount 
        discounted_session_total = session_cart_total - code.discount
    if discount > code.max_allowed_discount:
        discount = code.max_allowed_discount
        discounted_session_total = session_cart_total - code.max_allowed_discount
    if date.today() > code.expiry_date:
        return {'success': 'false','msg': 'Coupon code is expired',}
    return {'success': 'true', 'discounted_session_total': discounted_session_total, 'discount': discount}


class TotalListView(APIView):
    serializer_class = serializers.TotalSerializer

    def get(self, request, format=None):
        discount = {}
        session_cart_total = 0
        session = self.request.query_params.get('session')
        code = self.request.query_params.get('discount_code')
        email = self.request.query_params.get('email', ' ')

        if session is not None:
            _tax_cart_total(session)
            session_cart_total = _session_cart_total(session)
            response_dic = session_cart_total
            if code is not None:
                person = order_models.PersonalDetail.objects.filter(email_address=email).first()
                if email is None:
                    return Response({'msg': 'Please provide email adress to validate discount'}, status=status.HTTP_201_CREATED)
                code = order_models.Discount.objects.filter(code=code).first()
                if code is None :
                    return Response({'success': 'false', 'msg': 'Coupon is invalid'}, status=status.HTTP_201_CREATED)
                else:
                    if person is not None:
                        if person.used_voucher.filter(code=code).exists():
                            return Response({'success': 'false', 'msg': 'Coupon code is already used' }, status=status.HTTP_201_CREATED)
                discount = _calculate_discount(code, session_cart_total["session_cart_total"])
                if discount['success'] == 'false':
                    response_dic = dict(list(response_dic.items()) + list(discount.items()) + list({ 'discounted_session_total': response_dic['session_cart_total'], 'discount': 0 }.items()))
                    return Response(response_dic, status=status.HTTP_201_CREATED)
                response_dic = dict(list(response_dic.items()) + list(discount.items()) + list({'success': 'true', 'msg': 'Coupon is successfully applied'}.items()))
            return Response(response_dic, status=status.HTTP_201_CREATED)
        return Response({'msg':'session is requred field'}, status=status.HTTP_400_BAD_REQUEST)

def _get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except:
        return None


class DeliveryTimeView(generics.ListAPIView):
    queryset = order_models.DeliveryAddress.objects.all().order_by('updated_on')
    serializer_class = serializers.DeliveryTimeSerializer

    def get_queryset(self):
        queryset = self.queryset
        serializer = self.serializer_class(queryset)
        session = self.request.query_params.get('session')
        if session is not None:
            queryset = order_models.DeliveryAddress.objects.filter(session=session).all()
            return queryset
        return queryset


class DeliveryAddressViewSet(viewsets.ModelViewSet):
    queryset = order_models.DeliveryAddress.objects.all().order_by('updated_on')
    serializer_class = serializers.DeliveryAddressSerializer

    def get_queryset(self):
        queryset = self.queryset
        serializer = self.serializer_class(queryset)
        order_id = self.request.query_params.get('order_id')
        if order_id is not None:
            queryset = order_models.DeliveryAddress.objects.filter(order__order_id=order_id).all()
            return queryset
        return queryset

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            session = serializer.data.get('session')
            try:
                delivery_date = serializer.data.get('delivery_date')
                delivery_date = datetime.strptime(delivery_date,  "%Y-%m-%d")
                pickup_date = delivery_date + timedelta(weeks = order_models.CartItem.objects.filter(session=session).first().rental_int)
                pickup_adress, created = order_models.PickupAddress.objects.update_or_create(
                    session = session, 
                    defaults={'pickup_date': pickup_date,},)
            except:
                pass
            queryset, created = order_models.DeliveryAddress.objects.update_or_create(
                session = session, 
                defaults={'order': _get_or_none(order_models.OrderDetail, pk=serializer.data.get('order')),
                     'delivery_date': serializer.data.get('delivery_date'),
                     'delivery_address': serializer.data.get('delivery_address'),
                     'apt_number': serializer.data.get('apt_number'),
                     'description': serializer.data.get('description'),
                     'delivery_window_1': _get_or_none(admin_models.TimeSlots, pk=serializer.data.get('delivery_window_1')),
                     'delivery_window_2': _get_or_none(admin_models.TimeSlots, pk=serializer.data.get('delivery_window_2')),
                     'extra_work': _get_or_none(admin_models.ExtraWork, pk=serializer.data.get('extra_work')),
                        },)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PickupTimeView(generics.ListAPIView):
    queryset = order_models.PickupAddress.objects.all().order_by('updated_on')
    serializer_class = serializers.PickupTimeSerializer

    def get_queryset(self):
        queryset = self.queryset
        serializer = self.serializer_class(queryset)
        session = self.request.query_params.get('session')
        if session is not None:
            queryset = order_models.PickupAddress.objects.filter(session=session).all()
            return queryset
        return queryset


class PickupAddressViewSet(viewsets.ModelViewSet):
    queryset = order_models.PickupAddress.objects.all().order_by('updated_on')
    serializer_class = serializers.PickupAddressSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            session = serializer.data.get('session')
            queryset, created = order_models.PickupAddress.objects.update_or_create(
                session = session, 
                defaults={'order': _get_or_none(order_models.OrderDetail, pk=serializer.data.get('order')),
                     'pickup_date': serializer.data.get('pickup_date'),
                     'pickup_address': serializer.data.get('pickup_address'),
                     'apt_number': serializer.data.get('apt_number'),
                     'description': serializer.data.get('description'),
                     'pickup_window_1': _get_or_none(admin_models.TimeSlots, pk=serializer.data.get('pickup_window_1')),
                     'pickup_window_2': _get_or_none(admin_models.TimeSlots, pk=serializer.data.get('pickup_window_2')),
                     'extra_work': _get_or_none(admin_models.ExtraWork, pk=serializer.data.get('extra_work')),
                        },)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = self.queryset
        serializer = self.serializer_class(queryset)
        order_id = self.request.query_params.get('order_id')
        if order_id is not None:
            queryset = order_models.PickupAddress.objects.filter(order__order_id=order_id).all()
            return queryset
        return queryset


class AllCartListView(generics.ListAPIView):
    serializer_class = serializers.CartSerializer
    queryset = order_models.CartItem.objects.all()


class CartCreateView(generics.CreateAPIView):
    serializer_class = serializers.CartSerializer
    permission_classes = [AllowAny]
    queryset = order_models.CartItem.objects.all()


class PaymentDetailView(generics.CreateAPIView):
    serializer_class = serializers.PaymentDetailSerializer
    permission_classes = [AllowAny]
    queryset = order_models.PaymentDetail.objects.all()


def _generate_unique_code():
    code = admin_models.OrderIdPrefix.objects.first().prefix
    order = order_models.OrderDetail.objects.last()
    orderid = order.id + 1 if order is not None else 1
    while True:
        if order_models.OrderDetail.objects.filter(order_id=code+str(orderid)).count() == 0:
            return code + str(orderid)
        orderid = orderid + 1


class OrderCreateView(generics.CreateAPIView):
    serializer_class = serializers.OrderSerializer
    permission_classes = [AllowAny]
    queryset = order_models.OrderDetail.objects.all()

    def create(self, request):
        session = request.data.get('session')
        order_id = _generate_unique_code()
        status = "pend"
        delivery_date = request.data.get('delivery_date')
        voucher = request.data.get('voucher')
        order = order_models.OrderDetail.objects.create(
            order_id = order_id, delivery_date= delivery_date, status=status)
        total = _session_cart_total(session)
        order.total = total['session_cart_total']
        order.extra_work = total['extra_cost']
        order.tax = total['tax']
        cart_items = order_models.CartItem.objects.filter(session=session).all()
        delivery_address = order_models.DeliveryAddress.objects.filter(session=session).all()
        pickup_address = order_models.PickupAddress.objects.filter(session=session).all()

        fields = [cart_items, delivery_address, pickup_address]
        for field in fields:
            for i in field:
                if i:
                    i.session = str(order.id)
                    i.order = order
                    i.save()

        person_detail = order_models.PersonalDetail.objects.filter(session=session).first()
        person_detail.session = order.order_id
        order.ordered_by = person_detail
        if voucher != "":
            voucher = order_models.Discount.objects.get(code=voucher)
            order.used_voucher = voucher
            person_detail.used_voucher.add(voucher)
            discount = _calculate_discount(voucher, int(total['session_cart_total']))
            try: 
                order.total = discount['discounted_session_total']
                order.discount = discount['discount']
            except:
                pass
        order.save()
        return Response(self.serializer_class(order).data)

class UpdateRentalCreateView(generics.CreateAPIView):
    serializer_class = serializers.UpdateRentalSerializer
    queryset = order_models.CartItem.objects.all()
    permission_classes = [AllowAny]

class CartViewSet(viewsets.ModelViewSet):
    queryset = order_models.CartItem.objects.all()
    serializer_class = serializers.NewCartSerializer

class PersonalDetailsViewSet(viewsets.ModelViewSet):
    queryset = order_models.PersonalDetail.objects.all().order_by('updated_on')
    serializer_class = serializers.PersonalDetailsSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        serializer = self.serializer_class(queryset)
        order_id = self.request.query_params.get('order_id')
        if order_id is not None:
            order = order_models.OrderDetail.objects.get(order_id=order_id)
            queryset = order_models.PersonalDetail.objects.filter(orders=order.pk).all()
            return queryset
        return queryset

class PaymentDetailViewSet(viewsets.ModelViewSet):
    queryset = order_models.PaymentDetail.objects.all().order_by('updated_on')
    serializer_class = serializers.PaymentDetailSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        serializer = self.serializer_class(queryset)
        order_id = self.request.query_params.get('order')
        if order_id is not None:
            order = order_models.OrderDetail.objects.filter(order_id=order_id).first()
            if order_id is not None:
                queryset = order_models.PaymentDetail.objects.filter(order=order).all()
                return queryset
        return queryset

class ClearSession(APIView):
    serializer_class = serializers.TotalSerializer

    def get(self, request, format=None):
        session = self.request.query_params.get('session')
        if session is not None:
            cart_items = order_models.CartItem.objects.filter(session=session).all().delete()
            person = order_models.PersonalDetail.objects.filter(session=session).all().delete()
            delivery = order_models.DeliveryAddress.objects.filter(session=session).all().delete()
            pickup = order_models.PickupAddress.objects.filter(session=session).all().delete()
            return Response({'success': 'true', 'msg': 'Cart Cleared' }, status=status.HTTP_201_CREATED)
        return Response({'msg':'session is requred field'}, status=status.HTTP_400_BAD_REQUEST)