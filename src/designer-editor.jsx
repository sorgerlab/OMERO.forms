import React from 'react';
import Codemirror from 'react-codemirror';
import Select from 'react-select';
import 'codemirror/mode/javascript/javascript';
import { shouldRender } from 'react-jsonschema-form/lib/utils';
import defaultData from './designer-default';
const samples = {};
import Form from 'react-jsonschema-form';
import { Modal, Button, FormGroup, FormControl, ControlLabel, HelpBlock, Checkbox } from 'react-bootstrap'

// Patching CodeMirror#componentWillReceiveProps so it's executed synchronously
// Ref https://github.com/mozilla-services/react-jsonschema-form/issues/174
Codemirror.prototype.componentWillReceiveProps = function (nextProps) {
  if (this.codeMirror &&
      nextProps.value !== undefined &&
      this.codeMirror.getValue() != nextProps.value) {
    this.codeMirror.setValue(nextProps.value);
  }
  if (typeof nextProps.options === 'object') {
    for (var optionName in nextProps.options) {
      if (nextProps.options.hasOwnProperty(optionName)) {
        this.codeMirror.setOption(optionName, nextProps.options[optionName]);
      }
    }
  }
};

const log = (type) => console.log.bind(console, type);
const fromJson = (json) => JSON.parse(json);
const toJson = (val) => JSON.stringify(val, null, 2);

const cmOptions = {
  theme: 'default',
  height: 'auto',
  viewportMargin: Infinity,
  mode: {
    name: 'javascript',
    json: true,
    statementIndent: 2,
  },
  lineNumbers: true,
  lineWrapping: true,
  indentWithTabs: false,
  tabSize: 2,
};

class NameModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = { name: props.name || '' };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleExit = this.handleExit.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    const { name } = nextProps;
    this.setState({
      name
    });
  }

  handleChange(e) {
    this.setState({
      name: e.target.value
    });
  }

  handleSubmit(e) {
    e.preventDefault();
    const { onChange } = this.props;
    const name = this.state.name.trim();
    onChange(name);
  }

  handleExit() {
    const { name } = this.props;
    this.setState({
      name: name || ''
    });
  }

  render() {
    const { name } = this.state;
    const { show, toggle } = this.props;
    return (
      <Modal show={ show } onHide={ toggle } onExited={ this.handleExit }>
        <form onSubmit={ this.handleSubmit }>
          <Modal.Header closeButton>
            <Modal.Title>Modal heading</Modal.Title>
          </Modal.Header>
          <Modal.Body>
              <FormGroup
                controlId="formNameText"
              >
                <ControlLabel>Form Name</ControlLabel>
                <FormControl
                  type="text"
                  value={ name }
                  placeholder="Enter form name..."
                  onChange={ this.handleChange }
                />
                <FormControl.Feedback />
                <HelpBlock>This must be a unique string within the context of the OMERO instance. Forms can be overwritten by the original creator or an admin.</HelpBlock>
              </FormGroup>
          </Modal.Body>
          <Modal.Footer>
            <Button type="submit">Submit</Button>
            <Button onClick={ toggle }>Close</Button>
          </Modal.Footer>
        </form>
      </Modal>
    );
  }
}

class CodeEditor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {valid: true, code: props.code};
  }

  componentWillReceiveProps(props) {
    this.setState({valid: true, code: props.code});
  }

  shouldComponentUpdate(nextProps, nextState) {
    return shouldRender(this, nextProps, nextState);
  }

  onCodeChange = (code) => {
    this.setState({valid: true, code});
    setImmediate(() => {
      try {
        this.props.onChange(fromJson(this.state.code));
      } catch(err) {
        console.error(err);
        this.setState({valid: false, code});
      }
    });
  };

  render() {
    const { title } = this.props;
    const icon = this.state.valid ? 'ok' : 'remove';
    const cls = this.state.valid ? 'valid' : 'invalid';
    return (
      <div className='panel panel-default'>
        <div className='panel-heading'>
          <span className={`${cls} glyphicon glyphicon-${icon}`} />
          {' ' + title}
        </div>
        <Codemirror
          value={this.state.code}
          onChange={this.onCodeChange}
          options={Object.assign({}, cmOptions)} />
      </div>
    );
  }
}


export default class Editor extends React.Component {
  constructor(props) {
    super(props);

    const { schema, uiSchema, formData, validate } = defaultData;
    this.state = {
      form: undefined,
      schema,
      uiSchema,
      formData,
      validate,
      editor: 'default',
      liveValidate: true,
      formTypes: [],
      nameEdit: false
    };

    this.selectForm = this.selectForm.bind(this);
    this.selectTypes = this.selectTypes.bind(this);
    this.saveForm = this.saveForm.bind(this);
    this.toggleNameModal = this.toggleNameModal.bind(this);
    this.changeFormName = this.changeFormName.bind(this);

  }

  shouldComponentUpdate(nextProps, nextState) {
    return shouldRender(this, nextProps, nextState);
  }

  selectForm(selection) {
    const { forms } = this.props;

    if (selection && selection.value) {
      const form = forms[selection.value];
      if (form) {
        this.setState({
          form: form.formId,
          schema: form.jsonSchema,
          uiSchema: form.uiSchema,
          formData: {},
          formTypes: form.objTypes
        });
      }
    } else {
      const { schema, uiSchema, formData, validate } = defaultData;
      this.setState({
        form: undefined,
        schema,
        uiSchema,
        formData,
        validate,
        formTypes: []
      });
    }
  }

  selectTypes(selection) {
    this.setState({
      formTypes: selection.map(s => s.value)
    });
  }

  saveForm() {
    const { form, schema, uiSchema, formTypes } = this.state;
    const { forms, updateForm } = this.props;
    const request = new Request(
      this.props.urls.addForm,
      {
        method: 'POST',
        body: JSON.stringify({
          formId: form,
          jsonSchema: JSON.stringify(schema),
          uiSchema: JSON.stringify(uiSchema),
          objTypes: formTypes
        }),
        credentials: 'same-origin'
      }
    );

    fetch(request).then(() => {
      updateForm(form, schema, uiSchema, formTypes);
    });

  }

  onSchemaEdited   = (schema) => this.setState({schema});

  onUISchemaEdited = (uiSchema) => this.setState({uiSchema});

  onFormDataEdited = (formData) => this.setState({formData});

  setLiveValidate = () => this.setState({liveValidate: !this.state.liveValidate});

  onFormDataChange = ({formData}) => this.setState({formData});

  toggleNameModal(e) {
    if (e) {
      e.preventDefault();
    }
    const { nameEdit } = this.state;

    this.setState({
      nameEdit: !nameEdit
    });

  }

  changeFormName(name) {
    this.setState({
      form: name
    });
  }

  render() {
    const {
      form,
      schema,
      uiSchema,
      formData,
      liveValidate,
      validate,
      editor,
      formTypes,
      nameEdit
    } = this.state;
    const { forms } = this.props;
    const options = Object.keys(forms).map(key => {
      return {
        value: forms[key].formId,
        label: key
      };
    });

    const typeOptions = ['Project', 'Dataset', 'Screen', 'Plate'].map(t => ({
      value: t,
      label: t
    }));

    return (
      <div>

        <div className='col-sm-7'>

          {/* TODO Extract this into component */}
          <div className='panel panel-default'>
            <div className='panel-heading'>
                <Select
                  name='form-chooser'
                  placeholder='Load existing form...'
                  options={ options }
                  value={ form }
                  onChange={ this.selectForm }
                />
            </div>
            <div className='panel-body'>
              <div className='row'>
                <div className='col-sm-5'>
                  <Select
                    name='type-chooser'
                    placeholder='Select applicable types...'
                    multi={ true }
                    options={ typeOptions }
                    value={ formTypes }
                    onChange={ this.selectTypes }
                  />
                </div>
                <div className='col-sm-2'>
                  <Checkbox onChange={ this.setLiveValidate } checked={ liveValidate }>Live Validation</Checkbox>
                </div>
                <div className='col-sm-5'>
                  <button type='button' className='btn btn-info pull-right' onClick={ this.saveForm }>Save Form</button>
                </div>
              </div>
            </div>
          </div>

          <CodeEditor title='JSONSchema' theme={editor} code={toJson(schema)}
            onChange={this.onSchemaEdited} />
          <div className='row'>
            <div className='col-sm-6'>
              <CodeEditor title='UISchema' theme={editor} code={toJson(uiSchema)}
                onChange={this.onUISchemaEdited} />
            </div>
            <div className='col-sm-6'>
              <CodeEditor title='formData' theme={editor} code={toJson(formData)}
                onChange={this.onFormDataEdited} />
            </div>
          </div>
        </div>

        <div className='col-sm-5'>
          <Form
            liveValidate={liveValidate}
            schema={schema}
            uiSchema={uiSchema}
            formData={formData}
            onChange={this.onFormDataChange}
            validate={validate}
            onError={log('errors')} />
        </div>

        <NameModal
          name={ form }
          show={ nameEdit }
          toggle={ this.toggleNameModal }
          onChange={ this.changeFormName }
        />

      </div>
    );
  }
}
