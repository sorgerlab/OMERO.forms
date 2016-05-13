import React from 'react';
import ReactDOM from 'react-dom';
import AutoTagForm from './AutoTagForm';

function autotagform(imageIds, url, urlUpdate, urlCreateTag) {
  ReactDOM.render(
    <AutoTagForm url={url}
                 urlUpdate={urlUpdate}
                 urlCreateTag={urlCreateTag}
                 imageIds={imageIds} />,
    document.getElementById('auto_tag_panel')
  );
}

export default autotagform;
