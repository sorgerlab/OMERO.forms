import React from 'react';
import ReactDOM from 'react-dom';
import Forms from './Forms';

function omeroforms(datasetId, urlDatasetKeys, urlUpdate) {
  ReactDOM.render(
    <Forms urlDatasetKeys={urlDatasetKeys}
           urlUpdate={urlUpdate}
           datasetId={datasetId} />,
    document.getElementById('omero_forms_panel')
  );
}

export default omeroforms;
