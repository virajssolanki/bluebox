from django.urls import path, include
from pages import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'hdyfy', views.HDYFUListView)
router.register(r'contactus-info', views.ContactUsInfoListView)
router.register(r'contact', views.ContactListView)

urlpatterns = [
    path("faq/", views.FAQListView.as_view()),
    path("home/", views.HomeListView.as_view()),
    path("terms/", views.ServicesListView.as_view()),
    path("policy/", views.PolicyListView.as_view()),
    path("testimonials/", views.TestimonialListView.as_view()),
    path("why-us/", views.WhyChooseUsListView.as_view()),
    path('', include((router.urls))),
]
