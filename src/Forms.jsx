import React from 'react';
import ReactDOM from 'react-dom';

import Form from "react-jsonschema-form";
import './forms.css';

function compareFormData(d1, d2) {
  // No previous data
  if (d2 === undefined) {
    return true;
  }

  // Previous data, compare values
  for (var key in d1) {
      if (d1.hasOwnProperty(key)) {
        if (d1[key] !== d2[key]) {
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
          formSchema: JSON.parse(form.formSchema),
          formData: formData
        }
      });

      let activeFormId = undefined;
      if (jsonData.forms.length == 1) {
        activeFormId = jsonData.forms[0].formId;
      }

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

  switchForm(key) {

    this.setState({
      activeFormId: key
    });

  }

  // formData={ this.state.formData }
  render() {

    // If there is a single form which has previously been filled then
    // display that form directly.
    // Also, if there is only a single form for a group, display it directly

    const formChoices = [];
    for (var key in this.state.forms) {
        if (this.state.forms.hasOwnProperty(key)) {
          formChoices.push(
            <li className="omero_forms_list" key={ key } onClick={ this.switchForm.bind(this, key) }>{ key }</li>
          );
        }
    }

    let form;
    if (this.state.activeFormId !== undefined) {
      const activeForm = this.state.forms[this.state.activeFormId];

      form = (
        <Form
          schema={ activeForm.formSchema }
          formData = { activeForm.formData }
          onSubmit={ this.submitForm }
        />
      )
    }

    // Show list of available forms
    // <p>
    //   <ul>{ formChoices }</ul>
    // </p>

    return (
      (
        <div>
          { form }
        </div>

      )
    );
  }
}
