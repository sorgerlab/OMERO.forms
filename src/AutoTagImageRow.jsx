import React from 'react';
import AutoTagImageRowTokenCell from './AutoTagImageRowTokenCell';
import AutoTagImageRowTagCell from './AutoTagImageRowTagCell';

export default class AutoTagImageRow extends React.Component {

  // Only update an image row that has had a modified state
  shouldComponentUpdate(nextProps, nextState) {
    return (nextProps.showUnmapped !== this.props.showUnmapped ||
            nextProps.image !== this.props.image ||
            nextProps.tokenMap !== this.props.tokenMap);
  }

  render() {
    let image = this.props.image;
    let tokenMap = this.props.tokenMap;
    let unmappedTags = this.props.unmappedTags;
    let showUnmapped = this.props.showUnmapped;

    let cellNodesToken = [...tokenMap].map(kv => {
      let token = kv[1];
      let tag = token.activeTag;

      if (showUnmapped || token.possible.size > 0) {
        return (
          <AutoTagImageRowTokenCell key={token.value}
                                    image={image}
                                    token={token}
                                    tag={tag}
                                    cellCheckedChange={this.props.cellCheckedChange} />
        );
      }
    })

    let cellNodesTag = [...unmappedTags].map(tag =>
        <AutoTagImageRowTagCell key={tag.id}
                                image={image}
                                tag={tag}
                                cellCheckedChange={this.props.cellCheckedChange} />
    );

    return (
      <tr>
        {cellNodesToken}
        {cellNodesTag}
        <td style={{whiteSpace: 'nowrap'}}>{image.clientPath}&nbsp;({image.id})</td>
      </tr>
    );
  }
}
