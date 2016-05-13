Building OMERO.forms
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
