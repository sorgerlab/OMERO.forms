import django
from django.conf.urls import *

from . import views

urlpatterns = patterns(
    'django.views.generic.simple',

    url(r'^omeroforms/$',
        lambda x: None,
        name="omeroforms_base"),

    url(r'^omeroforms/dataset_keys/$',
        views.dataset_keys,
        name="omeroforms_dataset_keys"),

    # process form submission
    url(r'^omeroforms/submit/$',
        views.update,
        name="omeroforms_update"),

    # Designer App
    url(r'^omeroforms/designer',
        views.designer,
        name="omeroforms_designer"),

    url(r'^omeroforms/list_forms',
        views.list_forms,
        name="omeroforms_list_forms"),

    url(r'^omeroforms/add_form',
        views.add_form,
        name="omeroforms_add_form"),

    url(r'^omeroforms/assign_form',
        views.assign_form,
        name="omeroforms_assign_form"),

    url(r'^omeroforms/managed_groups',
        views.managed_groups,
        name="omeroforms_managed_groups"),

    url(r'^omeroforms/form_data/(?P<form_id>\w+)/(?P<obj_type>\w+)/(?P<obj_id>\w+)/$',
        views.form_data,
        name="omeroforms_form_data"),
)
