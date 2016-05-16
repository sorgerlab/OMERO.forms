import React from 'react';
import ReactDOM from 'react-dom';

import Form from "react-jsonschema-form";


export default class Forms extends React.Component {

  constructor() {
    super();

    this.state = {
      forms: [],
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
      console.log(jsonData);

      let forms = jsonData.forms.map(formString => JSON.parse(formString));
      console.log(forms);

      this.setState({
        forms: forms
      });

      console.log(jsonData);
    });
  }

  submitForm(formData) {
    console.log('submitform');
    console.log(formData);
  }

  // formData={ this.state.formData }
  render() {

    return (
      (
        this.state.forms.length > 0 &&
        <Form
          schema={ this.state.forms[0] }

          onSubmit={ this.submitForm }
        />
      )
    );
  }
}
