import React from 'react';
import Select from 'react-select';

import {union, intersection, difference} from './SetUtils';

export default class TagSelectModal extends React.Component {

  constructor() {
    super();

    this.state = {
      selected: null,
      status: ""
    }

    // Prebind this to callback methods
    this.selectTag = this.selectTag.bind(this);
    this.onSubmit = this.onSubmit.bind(this);

  }

  selectTag(val) {

    if (val.length === 0) {
      this.setState({
        selected: null
      });
    } else {
      this.setState({
        selected: val
      });
    }
  }

  onSubmit(e) {
    e.preventDefault();

    let addMapping = this.props.addMapping;
    let closeDialog = this.props.closeDialog;

    // If there is a selection, use that
    if (this.state.selected !== null) {
      console.log('There was a selection, using that');
      console.log(this.props.token);
      console.log(this.state.selected);
      console.log('---');
      // Resolve the selected tag ID to a tag and add the mapping
      addMapping(this.props.token, this.props.tags.get(this.state.selected.value));
      closeDialog(e);

    // Otherwise, create a new tag with the input unless there is a problem
    // with the input (e.g. existing tag value)
    } else if (this.refs.tagValue.value && this.refs.tagValue.value.trim().length > 0) {

      let tagValue = this.refs.tagValue.value.trim();
      let tagDescription = this.refs.tagDescription.value.trim();

      // Check and see if there is (at least one) tag with this existing value
      let exists = false;
      for (let kv of this.props.tags) {
        let tag = kv[1];
        if (tag.value === tagValue) {
          exists = true;
          break;
        }
      }

      if (exists) {
        this.setState({
          status: "It is inadvisable (and impossible in this interface) to create a tag with a value that already exists!"
        })

      // It's ok to add it
      } else {
        addMapping(this.props.token, null, tagValue, tagDescription);
        closeDialog(e);
      }

    // Unless there is no input in which case do nothing except maybe inform
    // the user that one or the other (or cancel) must be entered
    } else {
      this.setState({
        status: "Select either an existing tag, or enter a value for the new tag"
      })

      // Reset this in case it was all whitespace
      this.refs.tagValue.value = '';
    }


  }
  // TODO Make the Select options have the tag as the value instead of an ID so
  // then don't need to be looked up
  render() {

    // Get the tags that are already in use
    let usedTags = new Set();
    this.props.tokenMap.forEach(token => {
      usedTags = union(usedTags, token.possible)
    });

    let options = [...this.props.tags].filter(
      kv => !usedTags.has(kv[1])
    ).map(
      kv => {
        let tag = kv[1];
        return (
          {
            value: tag.id,
            label: "" + tag.value + "\u00a0" + "(" + tag.id + ")"
          }
        );
      }
    )

    // We use a 'button' instead of a 'submit' input to avoid the CSS styling
    // of submit which is overreaching from elsewhere.
    let formStyle= {
      width: "auto",
      minHeight: "0px",
      height: "258px"
    };

    return(
      <form className={"ui-dialog-content ui-widget-content"}
            scrolltop="0"
            scrollleft="0"
            style={formStyle}>
        <div className={"standard_form"}>

          <h1>Available Tags:</h1>

          <Select
              name="tagselect"
              placeholder="Select Tag"
              value={this.state.selected}
              options={options}
              onChange={this.selectTag}
          />

          <h1>OR Create a new tag:</h1>

          <label>Tag Name:</label>
          <input type="text" ref="tagValue" size="36" defaultValue={this.props.token.value} />

          <label>Description:</label>
          <textarea rows="3" cols="31" ref="tagDescription"></textarea>
        </div>

        <input type="button"
               value="OK"
               onClick={this.onSubmit} />

        <input type="button"
               value="Cancel"
               onClick={this.props.closeDialog} />

        <div className={"error"}>{this.state.status}</div>

      </form>
    );
  }

}
