import React from 'react';
import CodeMirror from 'react-codemirror2';
import Select from 'react-select';
import 'codemirror/mode/javascript/javascript';
import { shouldRender } from "@rjsf/core/lib/utils";
import defaultData from './designer-default';
const samples = {};
import Form from '@rjsf/core';
import { Modal, Button, FormGroup, FormControl, ControlLabel, HelpBlock, Checkbox } from 'react-bootstrap'

// Patching CodeMirror#componentWillReceiveProps so it's executed synchronously
// Ref https://github.com/mozilla-services/react-jsonschema-form/issues/174
CodeMirror.prototype.componentWillReceiveProps = function (nextProps) {
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
      formId: '',
      schema,
      uiSchema,
      formData,
      message: '',
      validate,
      editor: 'default',
      liveValidate: true,
      formTypes: [],
      editable: true,
      owners: [],
      exists: false,
      nameEdit: false,
      previousFormId: undefined,
      previousSchema: undefined,
      previousUISchema: undefined,
      previousFormTypes: undefined
    };

    this.selectForm = this.selectForm.bind(this);
    this.selectTypes = this.selectTypes.bind(this);
    this.saveForm = this.saveForm.bind(this);
    this.toggleNameModal = this.toggleNameModal.bind(this);
    this.changeFormName = this.changeFormName.bind(this);
    this.updateName = this.updateName.bind(this);
    this.updateMessage = this.updateMessage.bind(this);

  }

  shouldComponentUpdate(nextProps, nextState) {
    return shouldRender(this, nextProps, nextState);
  }

  loadForm(formId) {
    const { urls } = this.props;
    const formRequest = new Request(
      `${ urls.base }get_form/${ formId }/`,
      {
        credentials: 'same-origin'
      }
    );

    fetch(
      formRequest
    ).then(
      response => response.json()
    ).then(
      jsonData => {
        const form = jsonData.form;
        const schema = JSON.parse(form.schema);
        const uiSchema = JSON.parse(form.uiSchema);
        this.setState({
          timestamp: form.timestamp,
          schema,
          uiSchema,
          formData: {},
          formTypes: form.objTypes,
          editable: form.editable,
          owners: form.owners,
          exists: true,
          previousFormId: form.id,
          previousSchema: schema,
          previousUISchema: uiSchema,
          previousFormTypes: form.objTypes
        });
      }
    );
  }

  selectForm(selection) {
    const { forms } = this.props;
    if (selection && selection.value) {
      this.setState({
        formId: selection.value,
        message: ''
      });
      this.loadForm(selection.value);
    }
  }

  selectTypes(selection) {
    this.setState({
      formTypes: selection.map(s => s.value)
    });
  }

  saveForm() {
    const { formId, schema, uiSchema, formTypes, message } = this.state;
    const { forms, updateForm, urls } = this.props;

    const request = new Request(
      `${urls.base}save_form/`,
      {
        method: 'POST',
        body: JSON.stringify({
          id: formId,
          schema: JSON.stringify(schema),
          uiSchema: JSON.stringify(uiSchema),
          message,
          objTypes: formTypes
        }),
        credentials: 'same-origin'
      }
    );

    fetch(request).then(
      response => response.json()
    ).then(
      jsonData => {
        updateForm(jsonData.form)
        this.setState({
          message: '',
          previousSchema: schema,
          previousUISchema: uiSchema,
          previousFormTypes: formTypes
        });
      }
    );

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
      formId: name
    });
  }

  updateName(e) {
    const { urls } = this.props;
    const name = e.target.value;
    this.setState({
      formId: name
    });

    if (!name || name.length === 0) {
      this.setState({
        editable: true
      });
      return;
    }

    const request = new Request(
      `${urls.base}get_formid_editable/${ name }`,
      {
        credentials: 'same-origin'
      }
    );

    fetch(
      request
    ).then(
      response => response.json()
    ).then(
      jsonData => {
        this.setState({
          editable: jsonData.editable,
          owners: jsonData.owners,
          exists: jsonData.exists
        });
      }
    );

  }

  updateMessage(e) {
    this.setState({
      message: e.target.value
    });
  }

  render() {
    const {
      formId,
      schema,
      uiSchema,
      formData,
      message,
      liveValidate,
      validate,
      editor,
      formTypes,
      editable,
      exists,
      nameEdit,
      previousSchema,
      previousUISchema,
      previousFormTypes
    } = this.state;
    const { forms } = this.props;
    const options = Object.keys(forms).sort().map(key => {
      return {
        value: key,
        label: key
      };
    });

    const typeOptions = ['Project', 'Dataset', 'Screen', 'Plate'].map(t => ({
      value: t,
      label: t
    }));

    const unsaved = schema !== previousSchema || uiSchema !== previousUISchema || formTypes !== previousFormTypes;

    let editStatus = (
      <div className='alert alert-success form-small-alert'><strong>Valid form name{ exists && ' (Existing Form)'}</strong></div>
    );

    if (!formId || formId.length === 0) {
      editStatus = (
        <div className='alert alert-danger form-small-alert'><strong>Form must have a name</strong></div>
      );
    } else if (!editable) {
      editStatus = (
        <div className='alert alert-danger form-small-alert'><strong>Form name is owned by someone else</strong></div>
      );
    }


    return (
      <div>

        <div className='col-sm-7'>

          <div className='panel panel-default'>
            <div className='panel-heading'>
              <div className='row'>
                <div className='col-sm-4'>
                  <input
                    type='text'
                    className='form-control'
                    placeholder='Form name...'
                    value={ formId }
                    onChange={ this.updateName }
                  />
                </div>

                <div className='col-sm-2'>
                  <button
                    type='button'
                    className='btn btn-info'
                    onClick={ this.saveForm }
                    disabled={ !formId || !unsaved || !editable }
                  >
                    Save
                    { unsaved && <span class="badge">*</span> }
                  </button>
                </div>

                <div className='col-sm-4 col-sm-offset-2'>
                  <Select
                    name='form-chooser'
                    placeholder='Load existing form...'
                    options={ options }
                    onChange={ this.selectForm }
                  />
                </div>

              </div>

              <div className='row'>

                <div className='col-sm-10'>
                  { editStatus }
                </div>

                <div className='col-sm-2'>
                  <Checkbox onChange={ this.setLiveValidate } checked={ liveValidate }>Live Validation</Checkbox>
                </div>

              </div>

            </div>
            <div className='panel-body'>

              <div className='row'>
                <div className='col-sm-12'>
                  <div className='form-group'>
                    <label for='objTypes'>Object Types</label>
                    <Select
                      name='type-chooser'
                      placeholder='Select applicable types...'
                      multi={ true }
                      options={ typeOptions }
                      value={ formTypes }
                      onChange={ this.selectTypes }
                      id='objTypes'
                    />
                  </div>
                </div>
              </div>

              <div className='row'>
                <div className='col-sm-12'>
                  <div className='form-group'>
                    <label for='message'>Change Message</label>
                      <textarea
                        className='form-control'
                        rows='3'
                        placeholder='Enter a summary of the changes made...'
                        value={ message }
                        onChange={ this.updateMessage }
                        id='message'
                      />
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
          name={ formId }
          show={ nameEdit }
          toggle={ this.toggleNameModal }
          onChange={ this.changeFormName }
        />

      </div>
    );
  }
}
