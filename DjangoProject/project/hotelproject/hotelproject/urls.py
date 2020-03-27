from django.contrib import admin
from django.urls import path
from hotelinfo_app.views import index, resultPage,resultDetail, price_photo
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index),
    path('resultPage/', resultPage),
    path('resultDetail/', resultDetail),
    path('price_photo/', price_photo),
]
