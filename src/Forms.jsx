import React from 'react';
import ReactDOM from 'react-dom';

import Form from "react-jsonschema-form";


export default class Forms extends React.Component {

  constructor() {
    super();

    this.state = {
      form: {
        title: "Science stuff",
        type: "object",
        required: ["project", "someNumber"],
        properties: {
          project: {type: "string", title: "Project"},
          something: {type: "boolean", title: "Something?", default: false},
          someNumber: {"type": "number", "title": "Some number"}
        }
      },
      formData: {
        project: "Mega science thing",
        something: true,
        someNumber: 500
      },
      activeForm: undefined
    }

    this.submitForm = this.submitForm.bind(this);
    this.loadFromServer = this.loadFromServer.bind(this);
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
      console.log('DONE');
    });
  }

  submitForm(formData) {
    console.log('submitform');
    console.log(formData);
  }

  render() {
    return (
      <Form
        schema={ this.state.form }
        formData={ this.state.formData }
        onSubmit={ this.submitForm }
      />
    );
  }
}
