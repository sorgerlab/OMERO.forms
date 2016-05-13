import React from 'react';
import ReactTooltip from 'react-tooltip';
import Select from 'react-select';

export default class AutoTagHeaderRowTokenCell extends React.Component {

  constructor() {
    super();

    // Prebind this to callback methods
    this.handleCheckedChangeAll = this.handleCheckedChangeAll.bind(this);
    this.selectMapping = this.selectMapping.bind(this);
    this.formatTagLabel = this.formatTagLabel.bind(this);
    this.selectGetOptionLabel = this.selectGetOptionLabel.bind(this);
  }

  isChecked() {

    for (let image of this.props.images) {
      if (!image.checkedTokens.has(this.props.token)) {
        return false;
      }
    }
    return true;

  }

  isDisabled() {
    return this.props.tag === null;
  }

  handleCheckedChangeAll() {
    this.props.handleCheckedChangeAll(this.props.token, !this.isChecked());
  }

  formatTagLabel(tag) {
    if (tag !== undefined) {
      return "" + tag.value + "\u00a0" + "(" + tag.id + ")";
    }
    return '';
  }

  selectMapping(option) {
    if (option === null) {
      this.props.selectMapping(this.props.token, null);
    } else if (option.value !== undefined) {
      this.props.selectMapping(this.props.token, option.value);
    } else {
      this.props.newMapping(this.props.token)
    }
  }

  getTooltipId() {
    return 'tooltip-token-' + this.props.token.value;
  }

  selectGetOptionLabel(option) {
    let label = this.formatTagLabel(option);

    return (
      <span data-tip data-for={this.getTooltipId()}>{label}</span>
    )
	}

  render() {
    let token = this.props.token;
    let tag = this.props.tag;

    let options = [...token.possible].map(possibleTag =>
      {
        return (
          {
            value: possibleTag,
            label: this.formatTagLabel(possibleTag)
          }
        );
      }
    )

    let newExisting = (
      <span style={{color: "blue", fontWeight: "bold", borderStyle: "solid"}}>New/Existing Tag</span>
    );

    options.push({
      value: undefined,
      label: newExisting
    });

    let tagClassName = "tag_button";
    if (tag === null) {
      tagClassName += " tag_button_inactive";
    }

    return (
      <th>
        <div className={'token'}>{token.value}
          <input type="checkbox"
                 checked={this.isChecked()}
                 disabled={this.isDisabled()}
                 onChange={this.handleCheckedChangeAll} />
        </div>
        <div className={'tag'} >
          <Select
              name="tokenmapselect"
              onChange={this.selectMapping}
              options={options}
              value={tag}
              valueRenderer={this.selectGetOptionLabel}
              searchable={false}
              className={tagClassName}
              placeholder="&nbsp; "
          />
          {
            this.props.tag &&
            <ReactTooltip id={this.getTooltipId()} place="top" type="dark" effect="solid" class={"autotag_tooltip"}>
              <ul>
                <li><strong>ID:</strong> {this.props.tag.id}</li>
                <li><strong>Value:</strong> {this.props.tag.value}</li>
                {
                  this.props.tag.description &&
                  <li><strong>Description:</strong> {this.props.tag.description}</li>
                }
                <li><strong>Owner:</strong> {this.props.tag.owner.omeName}</li>
              </ul>
            </ReactTooltip>
          }
        </div>
      </th>
    );
  }
}
