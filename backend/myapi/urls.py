from xml.etree.ElementInclude import include
from django.urls import path

from myapi import views

urlpatterns = [
    path("test", views.test_connection, name="test_connection"),
    path("simulate", views.simulate, name="simulate"),
    path("defrag", views.defrag, name="defrag")
]
