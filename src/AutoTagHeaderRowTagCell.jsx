import React from 'react';
import ReactTooltip from 'react-tooltip';

export default class AutoTagHeaderRowTagCell extends React.Component {

  constructor() {
    super();

    // Prebind this to callback methods
    this.handleCheckedChangeAll = this.handleCheckedChangeAll.bind(this);
  }


  isChecked() {

    for (let image of this.props.images) {
      if (!image.checkedTags.has(this.props.tag)) {
        return false;
      }
    }
    return true;

  }

  handleCheckedChangeAll() {
    this.props.handleCheckedChangeAll(this.props.tag, !this.isChecked());
  }

  render() {
    let token = this.props.token;
    let tag = this.props.tag;

    let tooltipID = 'tooltip-tag-' + tag.id;

    return (
      <th>
        <div className={'token'}>test
          <input type="checkbox"
                 checked={this.isChecked()}
                 onChange={this.handleCheckedChangeAll} />
        </div>
        <div className={'tag'}>

            <span className={"tag_button tag_button_unmatched"}
               data-tip
               data-for={tooltipID}>{tag.value + "\u00a0" + "(" + tag.id + ")"}
            </span>
            <ReactTooltip id={tooltipID} place="top" type="dark" effect="solid" class={"autotag_tooltip"}>
              <ul>
                <li><strong>ID:</strong> {tag.id}</li>
                <li><strong>Value:</strong> {tag.value}</li>
                {
                  tag.description &&
                  <li><strong>Description:</strong> {tag.description}</li>
                }
                <li><strong>Owner:</strong> {tag.owner.omeName}</li>
              </ul>
            </ReactTooltip>

        </div>
      </th>
    );
  }
}
