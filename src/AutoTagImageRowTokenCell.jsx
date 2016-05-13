import React from 'react';

export default class AutoTagImageRowTokenCell extends React.Component {

  constructor() {
    super();

    // Prebind this to callback methods
    this.handleCheckedChange = this.handleCheckedChange.bind(this);
  }

  // Only update an image row cell that has an updated image or new map for
  // this column
  shouldComponentUpdate(nextProps, nextState) {
    return (
      // The image was updated AND this token is now checked/unchecked
      // whereas before it was unchecked/checked
      (
        nextProps.image !== this.props.image &&
        nextProps.image.checkedTokens.has(nextProps.token) !== this.props.image.checkedTokens.has(this.props.token)
      ) ||
      // The mapping of this column changed
      nextProps.tag !== this.props.tag ||
      // The image was updated AND this tag is now applied/unapplied
      // whereas before it was unapplied/applied
      (
        nextProps.image !== this.props.image &&
        nextProps.image.tags.has(nextProps.tag) !== this.props.image.tags.has(this.props.tag)
      )
    );
  }

  isTagged() {
    if (this.props.tag !== null && this.props.image.tags.has(this.props.tag)) {
      return true;
    }
    return false;

  }

  isChecked() {
    return this.props.image.checkedTokens.has(this.props.token);
  }

  isDisabled() {
    // No tag mapping active
    if (this.props.tag === null) {
      return true;
    }

    // No permissions to annotate
    return !(this.props.tag.canAnnotate() && this.props.image.canAnnotate());

  }

  handleCheckedChange() {
    this.props.cellCheckedChange(this.props.image, this.props.token);
  }

  render() {
    let className = '';
    if (this.isTagged()) {
      className = 'success';
    }

    return (
      <td className={className}>
        <input type="checkbox"
               checked={this.isChecked()}
               disabled={this.isDisabled()}
               onChange={this.handleCheckedChange} />
      </td>
    );
  }
}
