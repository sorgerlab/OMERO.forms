import React from 'react';
import ReactDOM from 'react-dom';
import Forms from './Forms';

function omeroforms(objId, objType, urlDatasetKeys, urlUpdate) {
  ReactDOM.render(
    <Forms urlDatasetKeys={ urlDatasetKeys }
           urlUpdate={ urlUpdate }
           objId={ objId }
           objType={ objType }/>,
    document.getElementById('omero_forms_panel')
  );
}

export default omeroforms;
