import React from 'react';
import Select from "react-select";
import Form from "react-jsonschema-form";

export default class Viewer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      formId: undefined,
      formData: []
    };

    this.selectForm = this.selectForm.bind(this);
  }

  selectForm(selection) {
    const { forms } = this.props;

    if (selection && selection.value) {
      const form = forms[selection.value];
      if (form) {
        this.setState({
          formId: form.formId,
          formData: []
        });
      }
    }
  }

  componentDidMount() {
    // this.getObjs();
    this.getData();
  }

  getData() {
    const { urls } = this.props;

    const request = new Request(
      `${urls.base}form_data/test1/Dataset/201`,
      {
        credentials: 'same-origin'
      }
    );

    fetch(
      request
    ).then(
      response => response.json()
    ).then(jsonData => {
      console.log(jsonData);
      return jsonData;
    }

    ).then(
      jsonData => this.setState({
        formData: jsonData.formData.map(d => JSON.parse(d['form_data']))
      })
    );
  }

  render() {
    const { formId, formData } = this.state;
    const { forms } = this.props;
    // const form = forms[formId];
    const form = forms['test1'];

    const formDataPoint = formData[formData.length-1];

    return (
      <div>
        <div className="col-sm-6"></div>
        <div className="col-sm-6">
          {
            formDataPoint &&
            <Form
              schema={ form.jsonSchema }
              uiSchema={ form.uiSchema }
              formData={ formDataPoint }
            />
          }

        </div>
      </div>
    );

  }
}
