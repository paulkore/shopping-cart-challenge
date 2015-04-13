from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from shopping_cart_challenge import views
from shopping_cart_challenge.views import ProductViewSet


api_router = routers.DefaultRouter()
api_router.register(r'products', ProductViewSet)


urlpatterns = patterns('',

    url(r'^$', views.info_view),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/', include(api_router.urls)),

    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

)
