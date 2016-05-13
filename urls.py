import django
from django.conf.urls import *

from . import views

urlpatterns = patterns(
    'django.views.generic.simple',

    url(r'^omeroforms/dataset_keys/$',
        views.dataset_keys,
        name="omeroforms_dataset_keys"),

    # process form submission
    url(r'^omeroforms/submit/$',
        views.update,
        name="omeroforms_update"),
)
