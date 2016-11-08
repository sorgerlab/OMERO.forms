import React from 'react';
import ReactDOM from 'react-dom';
import Viewer from './Viewer';

function omeroforms(objId, objType, urls) {
  ReactDOM.render(
    <Viewer
      objId={ objId }
      objType={ objType }
      urls={ urls }
    />,
    document.getElementById('omero_forms_panel')
  );
}

export default omeroforms;
