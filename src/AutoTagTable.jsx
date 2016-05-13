import React from 'react';
import ReactDOM from 'react-dom';

import AutoTagHeaderRow from './AutoTagHeaderRow';
import AutoTagImageRow from './AutoTagImageRow';

export default class AutoTagForm extends React.Component {

  shouldComponentUpdate(nextProps, nextState) {
    // If it is a change in the required token cardinality (and unmapped tags are displayed)
    if (
        this.props.showUnmapped &&
        nextProps.requiredTokenCardinality != this.props.requiredTokenCardinality &&
        this.props.images === nextProps.images
    ) {
      // Ensure it would actually result in a change of number of tags displayed
      return nextProps.tokenMap.size !== this.props.tokenMap.size;
    }

    // Always update for anything else
    return true;
  }

  render() {

    // Sort the rows by name, then ID
    let rowNodes = [...this.props.images].sort((a, b) => {
      let caselessA = a.name.toLowerCase();
      let caselessB = b.name.toLowerCase();

      if (caselessA < caselessB) {
        return -1;
      }
      if (caselessA > caselessB) {
        return 1;
      }
      if (a.id < b.id) {
        return -1;
      }
      if (a.id > b.id) {
        return 1
      }
      return 0;
    }).map(image =>
        <AutoTagImageRow key={image.id}
                         image={image}
                         tokenMap={this.props.tokenMap}
                         unmappedTags={this.props.unmappedTags}
                         cellCheckedChange={this.props.cellCheckedChange}
                         showUnmapped={this.props.showUnmapped} />
    );

    return (
      <div style={{position:'absolute',
                   bottom:'25px',
                   left:'0px',
                   top:'58px',
                   overflow:'auto',
                   marginTop:'0px',
                   right:'0px'}}>

        <table id="token-table"
               className={'table table-bordered table-striped table-hover table-condensed hidePathTokens hideExtTokens'}>
            <AutoTagHeaderRow tokenMap={this.props.tokenMap}
                              unmappedTags={this.props.unmappedTags}
                              selectMapping={this.props.selectMapping}
                              newMapping={this.props.newMapping}
                              images={this.props.images}
                              handleCheckedChangeAll={this.props.handleCheckedChangeAll}
                              showUnmapped={this.props.showUnmapped} />

          <tbody>
            {rowNodes}
          </tbody>

        </table>
      </div>
    );
  }
}
