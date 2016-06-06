import React from 'react';
import ReactDOM from 'react-dom';
import Select from 'react-select';
import Form from "react-jsonschema-form";
import 'react-select/dist/react-select.css';
import './forms.css';

function compareFormData(d1, d2) {
  // No previous data
  if (d2 === undefined) {
    return false;
  }

  // Previous data, compare values
  for (var key in d1) {
      if (d1.hasOwnProperty(key)) {
        if (d1[key] === Object(d1[key])) {
          if (!compareFormData(d1[key], d2[key])) {
            return false;
          }
        } else if (d1[key] !== d2[key]) {
          return false;
        }
      }
  }
  return true;
}

export default class Forms extends React.Component {

  constructor() {
    super();

    this.state = {
      forms: {},
      activeFormId: undefined
    }

    this.submitForm = this.submitForm.bind(this);
    this.loadFromServer = this.loadFromServer.bind(this);
    this.switchForm = this.switchForm.bind(this);
  }

  componentDidMount() {
    this.loadFromServer(this.props.datasetId);
  }

  componentWillReceiveProps(nextProps) {
    // If the dataset selected has changed, reload
    if (nextProps.datasetId !== this.props.datasetId) {
      this.loadFromServer(nextProps.datasetId);
      // Bail out as a reload was required and done
      return;
    }

  }

  loadFromServer(datasetId) {

    let loadRequest = $.ajax({
      url: this.props.urlDatasetKeys,
      type: "GET",
      data: { datasetId: datasetId },
      dataType: 'json',
      cache: false
    });

    loadRequest.done(jsonData => {

      let forms = {};
      jsonData.forms.forEach(form => {

        let formData;
        if (form.hasOwnProperty('formData')) {
          formData = JSON.parse(form.formData);
        }

        forms[form.formId] = {
          formId: form.formId,
          jsonSchema: JSON.parse(form.jsonSchema),
          uiSchema: JSON.parse(form.uiSchema),
          formData: formData
        }
      });

      let activeFormId = undefined;
      // if (jsonData.forms.length == 1) {
      //   activeFormId = jsonData.forms[0].formId;
      // }

      this.setState({
        forms: forms,
        activeFormId: activeFormId,
      });

    });
  }

  submitForm(formDataSubmission) {

    // If there are no changes, bail out as there is nothing to be done
    if (compareFormData(
      formDataSubmission.formData,
      this.state.forms[this.state.activeFormId].formData
    )) {
      return;
    }

    let updateForm = {
      'formData': JSON.stringify(formDataSubmission.formData),
      'formId': this.state.activeFormId,
      'datasetId': this.props.datasetId
    };

    // Take the form data, submit this to django
    $.ajax({
      url: this.props.urlUpdate,
      type: "POST",
      data: JSON.stringify(updateForm),
      success: function(data) {
        const form = this.state.forms[updateForm.formId];
        form.formData = formDataSubmission.formData
        this.setState({
          forms: this.state.forms
        })
        $("body").trigger("selection_change.ome");
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());

        // TODO Pop up a warning dialog

        // Completely reload as the state could have been partially updated
        // or failed for complex reasons due to updates outside of the scope
        // of autotag
        // this.refreshForm();

      }.bind(this)
    });
  }

  switchForm(options) {
    this.setState({
      activeFormId: options !== null ? options.value : undefined
    });
  }

  // formData={ this.state.formData }
  render() {

    // If there is a single form which has previously been filled then
    // display that form directly.
    // Also, if there is only a single form for a group, display it directly

    let options = [];
    for (let key in this.state.forms) {
      if (this.state.forms.hasOwnProperty(key)) {
        options.push({
          value: key,
          label: this.state.forms[key].jsonSchema.title
        });
      }
    }

    let form;
    if (this.state.activeFormId !== undefined) {
      const activeForm = this.state.forms[this.state.activeFormId];

      form = (
        <Form
          schema={ activeForm.jsonSchema }
          uiSchema={ activeForm.uiSchema }
          formData={ activeForm.formData }
          onSubmit={ this.submitForm }
        />
      )
    }

    return (
      (
        <div>

          <Select
              name="formselect"
              onChange={ this.switchForm }
              options={ options }
              value={ this.state.activeFormId }
              searchable={false}
              className={'form-switcher'}
          />

          { form }
        </div>

      )
    );
  }
}
