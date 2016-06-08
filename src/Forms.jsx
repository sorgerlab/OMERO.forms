import React from 'react';
import ReactDOM from 'react-dom';
import Select from 'react-select';
import Form from "react-jsonschema-form";
import 'react-select/dist/react-select.css';
import './forms.css';
import './bootstrap.css';

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
    this.loadFromServer(this.props.objId, this.props.objType);
  }

  componentWillReceiveProps(nextProps) {
    // If the object selected has changed, reload
    if (nextProps.objId !== this.props.objId ||
        nextProps.objType !== this.props.objType) {
      this.loadFromServer(nextProps.objId, nextProps.objType);
      // Bail out as a reload was required and done
      return;
    }

  }

  loadFromServer(objId, objType) {

    let loadRequest = $.ajax({
      url: this.props.urlDatasetKeys,
      type: "GET",
      data: { objId: objId, objType: objType },
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
      'objId': this.props.objId,
      'objType': this.props.objType
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
        });

        // Refresh the right panel
        $("body").trigger("selection_change.ome");

      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());

        // TODO What do do here?

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

    // TODO If there is no form title, use the form_id. Perhaps display the
    // form id anyway
    let options = [];
    for (let key in this.state.forms) {
      if (this.state.forms.hasOwnProperty(key)) {
        options.push({
          value: key,
          label: '' + (this.state.forms[key].jsonSchema.title || '') + ' (' + key + ')'
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
          <div className="row">
            <div className="col-sm-10 col-sm-offset-1">
              <Select
                  name="formselect"
                  onChange={ this.switchForm }
                  options={ options }
                  value={ this.state.activeFormId }
                  searchable={false}
                  className={'form-switcher'}
              />
            </div>
          </div>
          <div className="row">
            <div className="col-sm-10 col-sm-offset-1">
              <div className="panel panel-default">
                <div className="panel-body">
                  { form && form }
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    );
  }
}
