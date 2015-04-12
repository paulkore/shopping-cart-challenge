from django.conf.urls import patterns, include, url
from django.contrib import admin
from shopping_cart_challenge import views

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.info_view),

)
