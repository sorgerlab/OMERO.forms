import React from 'react';
import Select from "react-select";

export default class Assigner extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      formId: undefined,
      formGroupIds: []
    };

    this.selectForm = this.selectForm.bind(this);
    this.selectGroups = this.selectGroups.bind(this);
    this.saveAssignment = this.saveAssignment.bind(this);
  }

  selectForm(selection) {
    const { forms } = this.props;

    if (selection && selection.value) {
      const form = forms[selection.value];
      if (form) {
        this.setState({
          formId: form.formId,
          formGroupIds: form.groupIds
        });
      }
    }
  }

  selectGroups(selection) {
    this.setState({
      formGroupIds: selection.map(s => s.value)
    });
  }

  saveAssignment() {
    const { formId, formGroupIds } = this.state;
    const { forms, updateForm } = this.props;
    const request = new Request(
      this.props.urls.assignForm,
      {
        method: 'POST',
        body: JSON.stringify({
          formId: formId,
          groupIds: formGroupIds
        }),
        credentials: 'same-origin'
      }
    );

    fetch(request).then(() => {
      updateForm(formId, formGroupIds);
    });

  }

  render() {
    const { formId, formGroupIds } = this.state;
    const { forms, groups } = this.props;

    const formOptions = Object.keys(forms).map(key => {
      return {
        value: forms[key].formId,
        label: key
      };
    });

    const groupOptions = groups.map(group => ({
      value: group.id,
      label: `${group.name} (${group.id})`
    }));

    const form = formId ? forms[formId] : undefined;

    return (
      <div>
        <div className="row">
          <div className="col-sm-3">
            <Select
              name='form-chooser'
              placeholder='Select form...'
              options={ formOptions }
              value={ formId }
              onChange={ this.selectForm }
            />
          </div>
          <div className="col-sm-6">
            {
              form &&
              <Select
                name='group-chooser'
                placeholder='Select groups...'
                multi={ true }
                options={ groupOptions }
                value={ formGroupIds }
                onChange={ this.selectGroups }
              />
            }
          </div>
          <div className="col-sm-3">
            Summary
            { form && form.formId }
          </div>
        </div>

        <div className="row">
          <button type="button" className="btn btn-default" onClick={ this.saveAssignment }>Save</button>
        </div>
      </div>
    );
  }
}
