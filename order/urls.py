from django.urls import path, include
from order import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'delete_cart', views.CartViewSet)
router.register(r'delivery', views.DeliveryAddressViewSet)
router.register(r'pickup', views.PickupAddressViewSet)
router.register(r'personal_details', views.PersonalDetailsViewSet)
router.register(r'payment_details', views.PaymentDetailViewSet)

urlpatterns = [
    path('test-payment/', views.test_payment),
    path('save-stripe-info/', views.save_stripe_info),
    path("cart/<cart_sub_category>/<session>/", views.CartListView.as_view()),
    path("total/", views.TotalListView.as_view()),
    path("cart/<session>/", views.SessionCartListView.as_view()),
    path("delivery_time/", views.DeliveryTimeView.as_view()),
    path("pickup_time/", views.PickupTimeView.as_view()),
    path("cart/update_rental", views.UpdateRentalCreateView.as_view()),
    path("cart/add", views.CartCreateView.as_view()),
    path("add/payment_details", views.PaymentDetailView.as_view()),
    path("add", views.OrderCreateView.as_view()),
    path("clear_cart/", views.ClearSession.as_view()),
    path("preview/", views.OrderListView.as_view()),
    path('', include((router.urls))),
]