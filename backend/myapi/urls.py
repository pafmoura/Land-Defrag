from xml.etree.ElementInclude import include
from django.urls import path

from myapi import views

urlpatterns = [
    path("test", views.test_connection, name="test_connection"),
    path("simulate", views.simulate, name="simulate"),
    path("defrag", views.defrag, name="defrag"),
    path("processes/<path:generated_file_name>", views.get_states_defrag, name="processes_with_file"),
    path("processes", views.get_states_defrag, name="processes"),
    path("get_simulation_by_filename/<path:generated_file_name>/", views.get_simulation_by_filename, name="get_simulation_by_filename"),
]
