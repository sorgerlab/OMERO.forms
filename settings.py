# This settings.py file will be imported by omero.settings file AFTER it has initialised custom settings.
# import django

# https://www.openmicroscopy.org/site/support/omero5.2/developers/Web/CreateApp.html
CUSTOM_SETTINGS_MAPPINGS = {
    "omero.web.forms.priv.uid": [
        "OMERO_FORMS_PRIV_UID",
        None,
        long,
        "The priviledged user id to be used for storing key-values"
    ],
    "omero.web.forms.priv.password": [
        "OMERO_FORMS_PRIV_PASSWORD",
        None,
        str,
        "The priviledged user's password to be used for storing key-values"
    ],
}
