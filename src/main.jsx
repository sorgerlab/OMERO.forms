import React from 'react';
import ReactDOM from 'react-dom';
import AutoTagForm from './AutoTagForm';

function omeroforms(datasetId, url, urlUpdate) {
  ReactDOM.render(
    <AutoTagForm url={url}
                 urlUpdate={urlUpdate}
                 datasetId={datasetId} />,
    document.getElementById('omero_forms_panel')
  );
}

export default omeroforms;
