Installation
============

Documentation for using PYTHONPATH to allow omero to find webapps is [here](https://www.openmicroscopy.org/site/support/omero5/developers/Web/CreateApp.html#add-your-app-location-to-your-pythonpath).

Before configuring the plugin, create an administrative user in OMERO. In this example that user is called 'formmaster'. This user should not be a member of any groups other than the 'system' group that all administrators are a part of. Give this user a secure password.

Perform the installation steps

```sh
# Clone the repository in to a location outside of the Omero.web installation, e.g. `~/Checkout/forms`
cd Checkout
git clone https://github.com/dpwrussell/OMERO.forms.git forms

# Add this location to the PYTHONPATH
export PYTHONPATH=~/Checkout/forms:$PYTHONPATH

# Add OMERO.forms to webclient
omero config append omero.web.apps '"forms"'

# Add OMERO.forms to centre panel
omero config append omero.web.ui.center_plugins '["Forms", "forms/forms_init.js.html", "omero_forms_panel"]'

# Add a top-link to the OMERO.forms designer. Note: This example would remove any other
omero config append omero.web.ui.top_links '["Forms Designer", "omeroforms_designer", {"title": "Open OMERO.Forms in a new tab", "target": "new"}]'

# Configure the form master user
omero config set omero.web.forms.priv.user 'formmaster'
omero config set omero.web.forms.priv.password 'changeit'
```

Contributing
================

OMERO.forms uses node and webpack.

Building for production
=======================

This will build `static/forms/js/bundle.js` which contains basically the whole
project including CSS. It is minified.

``` bash
npm install
node_modules/webpack/bin/webpack.js -p
```

Building for development
========================

This will detect changes and rebuild `static/forms/js/bundle.js` when there
are any. This works in conjunction with django development server as that
will be monitoring `bundle.js` for any changes.

``` bash
npm install
node_modules/webpack/bin/webpack.js --watch
```
