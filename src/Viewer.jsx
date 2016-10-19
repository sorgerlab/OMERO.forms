import React from 'react';
import Forms from './Forms';
import History from './History';

import 'react-select/dist/react-select.css';
import './forms.css';
import './bootstrap.css';

export default class Viewer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      mode: 'Editor'
    };

    this.selectMode = this.selectMode.bind(this);
  }

  selectMode(mode) {
    this.setState({
      mode: mode
    });
  }

  renderNav() {
    const { mode } = this.state;

    const items = ['Editor', 'History'].map(m => {
      return (
        <li className={ m === mode ? 'active' : '' }>
          <a href='#' onClick={ () => this.selectMode(m) }>{ m }</a>
        </li>
      );
    })

    return (
      <ul className="nav nav-tabs">
        { items }
      </ul>
    )
  }

  renderMode() {
    const { mode } = this.state;
    const { urls, urlDatasetKeys, urlUpdate, objId, objType } = this.props;
    if (mode === 'Editor') {
      return (
        <Forms urlDatasetKeys={ urlDatasetKeys }
               urlUpdate={ urlUpdate }
               objId={ objId }
               objType={ objType }/>
      );
    } else if (mode === 'History') {
      return (
        <History
          urls={ urls }
          objType={ objType }
          objId={ objId }
        />
      );
    }
  }

  render() {
    return (
      <div>
        { this.renderNav() }
        { this.renderMode() }
      </div>
    );

  }
}
