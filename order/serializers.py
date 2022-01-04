from rest_framework import fields, serializers
from order import models
from store import models as store_models
from settingadmin import models as admin_models
from store import serializers as store_serializers

class TimeSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = admin_models.TimeSlots
        fields = ['start_time', 'end_time']

class DiscountSerializer(serializers.ModelSerializer):
    session = serializers.CharField(max_length=60, required=False)
    class Meta:
        model = models.Discount
        fields = ['session', 'code']

class NewCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = "__all__"

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryAddress
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        try:
            response['delivery_window_1'] = TimeSlotsSerializer(instance.delivery_window_1).data
            response['delivery_window_2'] = TimeSlotsSerializer(instance.delivery_window_2).data
            response['extrawork'] = store_serializers.ExtraWorkSerializer(instance.extra_work).data        
        except:
            pass
        return response

class PickupAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PickupAddress
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        try:
            response['pickup_window_1'] = TimeSlotsSerializer(instance.pickup_window_1).data
            response['pickup_window_2'] = TimeSlotsSerializer(instance.pickup_window_2).data
            response['extrawork'] = store_serializers.ExtraWorkSerializer(instance.extra_work).data
        except:
            pass
        return response

class DeliveryTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryAddress
        fields = ['session', 'delivery_window_1', 'delivery_window_2', 'delivery_date']
        depth = 1

class PickupTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PickupAddress
        fields = ['session', 'pickup_window_1', 'pickup_window_2', 'pickup_date']
        depth = 1

class HDFYUSerializer(serializers.ModelSerializer):
    class Meta:
        model = admin_models.HDYFU
        fields = '__all__'
        
class PersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonalDetail
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        try:
            response['hdyfu'] = HDFYUSerializer(instance.hdyfu).data
            response['used_voucher'] = DiscountSerializer(instance.used_voucher).data
        except:
            pass
        return response

class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentDetail
        fields = '__all__'
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = store_models.Product
        fields = "__all__"

class TotalSerializer(serializers.Serializer):
    session_cart_total = serializers.IntegerField()

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discount
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    cart_items = NewCartSerializer(many=True)
    delivery_adress = DeliveryAddressSerializer()
    pickup_adress = PickupAddressSerializer()
    ordered_by = PersonalDetailsSerializer()
    payment_details = PaymentDetailSerializer()
    used_voucher = DiscountSerializer()
    
    class Meta:
        model = models.OrderDetail
        fields = "__all__"

class EmailCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['product', 'cart_price', 'rental', 'quantity']
        depth = 1

class CartSerializer(serializers.ModelSerializer):
    cart_main_category = serializers.PrimaryKeyRelatedField(
        queryset=store_models.Category.objects.all(), write_only=True
    )
    cart_sub_category = serializers.PrimaryKeyRelatedField(
        queryset=store_models.SubCategory.objects.all(), write_only=True
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=store_models.Product.objects.all(), write_only=True
    )
    session_cart_total = serializers.SerializerMethodField()

    def cart_price(self, validated_data):
        moving_price = { "1 Week": 1, "2 Week": 2, "3 Week": 3, "4 Week": 4, "5 Week": 5, "6 Week": 6, }
        product = validated_data.get('product')
        rental = validated_data.get('rental')
        if product.product_sub_category.title == 'Moving Supplies':
            query = store_models.PriceManagement.objects.filter(rental=rental).first()
            cart_price = product.price*moving_price[query.rental.period]
            return cart_price

        elif product.product_sub_category.title == 'Packing Supplies':
            cart_price = product.price
            return cart_price
            
        else:
            query = store_models.PriceManagement.objects.filter(product=product).filter(rental=validated_data.get('rental')).all()
            for i in query:
                cart_price = i.price
                return cart_price

    def create(self, validated_data):
        cart_main_category = validated_data.get('cart_main_category')
        cart_sub_category = validated_data.get('cart_sub_category')
        session = validated_data.get('session')
        quantity = validated_data.get('quantity')
        product = validated_data.get('product')
        rental = validated_data.get('rental')
        cart_price = self.cart_price(validated_data)

        #if product is a box product remove existing box products and add new
        if cart_sub_category.title == 'Box Packages':
            queryset, created = models.CartItem.objects.update_or_create(
                session = session,
                cart_sub_category = cart_sub_category,
                defaults={'cart_price': cart_price, 
                            'product' : product,
                            'cart_main_category':cart_main_category,
                            'rental':rental,
                                                },
            )
            return queryset
        #if product is not box product don't remove existing box products and add new
        else:
            try:
                quantity += models.CartItem.objects.get(session=session, product=product).quantity
            except:
                pass
            queryset, created = models.CartItem.objects.update_or_create(
                session = session,
                product = product,
                defaults={'quantity': quantity, 'cart_price': cart_price, 
                                                'cart_main_category':cart_main_category,
                                                'cart_sub_category':cart_sub_category,
                                                'rental':rental,
                                                'inital_price': product.price,
                                                },
            )
            return queryset

    def get_session_cart_total(self, obj):
        cart_items = models.CartItem.objects.filter(session=self.context['request'].path.split('/')[-2]).all()
        session_cart_total = 0
        for i in cart_items:
            session_cart_total += i.cart_price
        return session_cart_total

    def to_representation(self, value):
        data = super().to_representation(value)  
        mode_serializer = ProductSerializer(value.product)
        data['product'] = mode_serializer.data
        return data

    class Meta:
        model = models.CartItem
        fields = '__all__'


class UpdateRentalSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        moving_price = {
        "1 Week": 1,
        "2 Week": 2,
        "3 Week": 3,
        "4 Week": 4,
        "5 Week": 5,
        "6 Week": 6,
        }
        session = validated_data.get('session')
        rental = validated_data.get('rental')
        queryset = models.CartItem.objects.filter(session=session).all()
        for item in queryset:
            if item.cart_sub_category.title == 'Box Packages':
                query = store_models.PriceManagement.objects.filter(product=item.product).get(rental=rental)
                item.cart_price = query.price
                item.rental = query.rental.id
                item.save()
            elif item.cart_sub_category.title == 'Moving Supplies':
                query = store_models.PriceManagement.objects.filter(rental=rental).first()
                item.cart_price = item.inital_price*moving_price[query.rental.period]
                item.rental = query.rental.id
                item.save()
            else:
                pass
        return queryset

    class Meta:
        model = models.CartItem
        fields = ['session', 'rental']
