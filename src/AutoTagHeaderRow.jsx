import React from 'react';

import AutoTagHeaderRowTokenCell from './AutoTagHeaderRowTokenCell';
import AutoTagHeaderRowTagCell from './AutoTagHeaderRowTagCell';

export default class AutoTagHeaderRow extends React.Component {
  render() {
    let cellNodesToken = [...this.props.tokenMap].map(kv => {
      let token = kv[1];
      let tag = token.activeTag;

      // Hide the unmapped columns if set
      if (this.props.showUnmapped || token.possible.size > 0) {
        return (
          <AutoTagHeaderRowTokenCell token={token}
                                     tag={tag}
                                     tokenMap={this.props.tokenMap}
                                     selectMapping={this.props.selectMapping}
                                     newMapping={this.props.newMapping}
                                     images={this.props.images}
                                     handleCheckedChangeAll={this.props.handleCheckedChangeAll}
                                     key={token.value} />
        )
      }

    });

    let cellNodesTag = [...this.props.unmappedTags].map(tag =>
      <AutoTagHeaderRowTagCell tag={tag}
                               images={this.props.images}
                               handleCheckedChangeAll={this.props.handleCheckedChangeAll}
                               key={tag.id} />
    );

    return (
      <thead>
        <tr>
          {cellNodesToken}
          {cellNodesTag}
          <th>Original Import Path</th>
        </tr>
      </thead>
    );
  }
}
