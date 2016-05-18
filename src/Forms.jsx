import React from 'react';
import ReactDOM from 'react-dom';

import Form from "react-jsonschema-form";


export default class Forms extends React.Component {

  constructor() {
    super();

    this.state = {
      forms: {},
      formData: {
        project: "Mega science thing",
        something: true,
        someNumber: 500
      },
      activeFormId: undefined
    }

    this.submitForm = this.submitForm.bind(this);
    this.loadFromServer = this.loadFromServer.bind(this);
    this.switchForm = this.switchForm.bind(this);
  }

  componentDidMount() {
    this.loadFromServer(this.props.datasetId, 1);
  }

  loadFromServer(datasetId, groupId) {

    console.log('Loading from server');

    let loadRequest = $.ajax({
      url: this.props.urlDatasetKeys,
      type: "GET",
      data: { datasetId: datasetId },
      dataType: 'json',
      cache: false
    });

    loadRequest.done(jsonData => {
      console.log(jsonData);

      let forms = {};
      jsonData.forms.forEach(form => {
        forms[form.form_id] = {
          form_id: form.form_id,
          form_schema: JSON.parse(form.form_json)
        }
      });

      let activeFormId = undefined;
      if (jsonData.forms.length == 1) {
        activeFormId = jsonData.forms[0].form_id;
      }

      this.setState({
        forms: forms,
        activeFormId: activeFormId
      });

    });
  }

  submitForm(formDataSubmission) {
    console.log('submitform');
    console.log(formDataSubmission);

    let updateForm = {
      'formData': formDataSubmission.formData,
      'formId': this.state.activeFormId,
      'datasetId': this.props.datasetId
    };

    // Take the form data, submit this to django
    $.ajax({
      url: this.props.urlUpdate,
      type: "POST",
      data: JSON.stringify(updateForm),
      success: function(data) {
        // No action required
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
            <li key={ key } onClick={ this.switchForm.bind(this, key) }>{ key }</li>
          );
        }
    }

    let form;
    if (this.state.activeFormId !== undefined) {
      const activeForm = this.state.forms[this.state.activeFormId];

      form = (
        <Form
          schema={ activeForm.form_schema }

          onSubmit={ this.submitForm }
        />
      )
    }



    return (
      (
        <div>
          <ul>{ formChoices }</ul>
          { form }
        </div>

      )
    );
  }
}
