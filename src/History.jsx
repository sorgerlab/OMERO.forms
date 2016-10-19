import React from 'react';
import ReactDOM from 'react-dom';
import Select from 'react-select';
import Form from "react-jsonschema-form";

export default class History extends React.Component {

  constructor() {
    super();

    this.state = {
      forms: {},
      formId: undefined,
      formData: [],
      dataIndex: undefined
    }

    this.loadFromServer = this.loadFromServer.bind(this);
    this.switchForm = this.switchForm.bind(this);
    this.switchData = this.switchData.bind(this);
  }

  componentDidMount() {
    this.loadFromServer();
  }

  componentWillReceiveProps(nextProps) {
    // If the object selected has changed, reload
    if (nextProps.objId !== this.props.objId ||
        nextProps.objType !== this.props.objType) {
      this.loadFromServer();
      this.getData();
      // Bail out as a reload was required and done
      return;
    }

  }

  loadFromServer() {

    const { urls, objType, objId } = this.props;

    let loadRequest = $.ajax({
      url: urls.urlDatasetKeys,
      type: "GET",
      data: { objId: objId, objType: objType },
      dataType: 'json',
      cache: false
    });

    loadRequest.done(jsonData => {

      let forms = {};
      jsonData.forms.forEach(form => {

        forms[form.formId] = {
          formId: form.formId,
          jsonSchema: JSON.parse(form.jsonSchema),
          uiSchema: JSON.parse(form.uiSchema)
        }
      });

      this.setState({
        forms: forms,
        formId: Object.keys(forms).length === 1 ? forms[Object.keys(forms)[0]].formId : undefined
      });

      if (Object.keys(forms).length === 1) {
        this.getData();
      }

    });
  }

  getData() {
    const { formId } = this.state;
    const { urls, objType, objId } = this.props;

    const request = new Request(
      `${urls.base}form_data/${formId}/${objType}/${objId}`,
      {
        credentials: 'same-origin'
      }
    );

    fetch(
      request
    ).then(
      response => response.json()
    ).then(
      jsonData => this.setState({
        formData: jsonData.formData.sort((a, b) => a >= b),
        dataIndex: jsonData.formData.length-1
      })
    );
  }

  switchForm(options) {
    this.setState({
      formId: options !== null ? options.value : undefined
    });
  }

  switchData(options) {
    this.setState({
      dataIndex: options.target.value
    });
  }

  render() {

    const { formId, formData, dataIndex } = this.state;

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
    if (formId !== undefined) {
      const activeForm = this.state.forms[formId];

      form = (
        <Form
          schema={ activeForm.jsonSchema }
          uiSchema={ activeForm.uiSchema }
          formData={ dataIndex !== undefined ? JSON.parse(formData[dataIndex].form_data) : undefined }
        >
          <button type="button" className="btn btn-primary disabled">Submit</button>
        </Form>
      )
    }

    // <Select
    //   name="dataselect"
    //   onChange={ this.switchData }
    //   options={ formData.map((d, i) => ({
    //     value: i,
    //     label: `${d.changed_by}_${d.changed_at}`
    //   })) }
    //   value={ dataIndex }
    //   searchable={ false }
    // />

    return (
      (
        <div className="container-fluid">
          <div className="row">
            <div className="col-sm-10 col-sm-offset-1">
              <Select
                  name="formselect"
                  onChange={ this.switchForm }
                  options={ options }
                  value={ formId }
                  searchable={false}
                  className={'form-switcher'}
              />
            </div>
          </div>
          <div className="row">
            <div className="col-sm-10 col-sm-offset-1">
              { formData && dataIndex &&
                `${formData[dataIndex].changed_by} - ${formData[dataIndex].changed_at}`
              }
              {
                formData && dataIndex &&
                <input type="range" id="dataselect" min="0" max={ Object.keys(formData).length-1 } className="form-control" onInput={ this.switchData } value={ dataIndex }/>
              }
            </div>
          </div>
          <div className="row">
            <div className="col-sm-10 col-sm-offset-1">

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
