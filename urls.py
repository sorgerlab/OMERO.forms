import django
from django.conf.urls import *

from . import views

urlpatterns = patterns(
    'django.views.generic.simple',

    # Designer App
    url(r'^designer/$',
        views.designer,
        name='omeroforms_designer'),

    # API
    url(r'^$',
        lambda x: None,
        name='omeroforms_base'),

    # List all forms
    url(r'^list_forms/$',
        views.list_forms,
        name='omeroforms_list_forms'),

    # List the forms that are assigned to the user's active group that
    # apply to the object type
    url(r'^list_applicable_forms/(?P<obj_type>\w+)/$',
        views.list_applicable_forms,
        name='omeroforms_list_applicable_forms'),

    # Get a form (latest version)
    url(r'^get_form/(?P<form_id>[\w ]+)/$',
        views.get_form,
        name='omeroforms_get_form'),

    # Get data for a form (latest version) for a certain object
    url(r'^get_form_data/'
        r'(?P<form_id>\w+)/(?P<obj_type>\w+)/(?P<obj_id>[\w ]+)/$',
        views.get_form_data,
        name='omeroforms_get_form_data'),

    # Get assignments (restricted to those the user can unassign)
    url(r'get_form_assignments/$',
        views.get_form_assignments,
        name='omeroforms_get_form_assignments'),

    # Get the entire history of a form including all data and the forms used
    # to enter that data
    url(r'^get_form_data_history/'
        r'(?P<form_id>\w+)/(?P<obj_type>\w+)/(?P<obj_id>[\w ]+)/$',
        views.get_form_data_history,
        name='omeroforms_get_form_data_history'),

    # Get groups that the user can manage
    url(r'^get_managed_groups/$',
        views.get_managed_groups,
        name='omeroforms_get_managed_groups'),

    # Lookup usernames by uid
    url(r'^get_users/$',
        views.get_users,
        name='omeroforms_get_users'),

    # Save a form version (potentially a new form)
    url(r'^save_form/$',
        views.save_form,
        name='omeroforms_save_form'),

    # Save data for a form
    url(r'^save_form_data/'
        r'(?P<form_id>\w+)/(?P<obj_type>\w+)/(?P<obj_id>[\w ]+)/$',
        views.save_form_data,
        name='omeroforms_save_form_data'),

    # Save a form assignment
    url(r'^save_form_assignment/$',
        views.save_form_assignment,
        name='omeroforms_save_form_assignment'),
)
