import django
from django.conf.urls import *

from . import views

urlpatterns = patterns(
    'django.views.generic.simple',

    url(r'^omeroforms/main/$',
        views.main,
        name="omeroforms_main"),

    # process form submission
    url(r'^omeroforms/submit/$',
        views.update,
        name="omeroforms_update"),
)
