from django.urls import path
from store import views


urlpatterns = [
    path("rentals/", views.RentalListView.as_view()),
    path("products/<main_category>/<sub_category>/<rental>/", views.BoxPackgeListView.as_view()),
    path("products/<main_category>/<sub_category>/", views.ProductListView.as_view()),
    path("locations/", views.LocationListView.as_view()),
    path("quote/", views.QuoteCreateView.as_view()),
    path("news-letter/", views.NewsletterCreateView.as_view()),
    path("check-zipcode/", views.CheckZipCode.as_view()),
    path("check-adress/", views.CheckAdress.as_view()),
    path("delivery-windows/", views.DeliveryWindowsView.as_view()),
    path("extra-work/", views.ExtraWorkListView.as_view()),
    path("unavailable_dates/", views.UnavailableDattesListView.as_view()),
]
