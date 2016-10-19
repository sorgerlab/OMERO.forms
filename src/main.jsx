import React from 'react';
import ReactDOM from 'react-dom';
import Viewer from './Viewer';

function omeroforms(objId, objType, urlDatasetKeys, urlUpdate, urls) {
  ReactDOM.render(
    <Viewer urlDatasetKeys={ urlDatasetKeys }
           urlUpdate={ urlUpdate }
           objId={ objId }
           objType={ objType }
           urls={ urls }
    />,
    document.getElementById('omero_forms_panel')
  );
}

export default omeroforms;
