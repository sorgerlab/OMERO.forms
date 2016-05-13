import React from 'react';

export default class AutoTagImageRowTagCell extends React.Component {

  constructor() {
    super();

    // Prebind this to callback methods
    this.handleCheckedChange = this.handleCheckedChange.bind(this);
  }

  shouldComponentUpdate(nextProps, nextState) {
    return (
      // The image was updated AND this tag is now checked/unchecked
      // whereas before it was unchecked/checked
      (
        nextProps.image !== this.props.image &&
        nextProps.image.checkedTags.has(nextProps.tag) !== this.props.image.checkedTags.has(this.props.tag)
      ) ||
      // The image was updated AND this tag is now applied/unapplied
      // whereas before it was unapplied/applied
      (
        nextProps.image !== this.props.image &&
        nextProps.image.tags.has(nextProps.tag) !== this.props.image.tags.has(this.props.tag)
      )
    );
  }

  isTagged() {
    return this.props.image.tags.has(this.props.tag);
  }

  isChecked() {
    return this.props.image.checkedTags.has(this.props.tag);
  }

  isDisabled() {
    // No permissions to annotate
    return !(this.props.tag.canAnnotate() && this.props.image.canAnnotate());
  }

  handleCheckedChange() {
    this.props.cellCheckedChange(this.props.image, this.props.tag);
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
               onChange={this.handleCheckedChange} />
      </td>
    );
  }
}
