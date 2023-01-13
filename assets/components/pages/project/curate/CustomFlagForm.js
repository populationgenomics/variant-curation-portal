import PropTypes from "prop-types";
import React from "react";
import { connect } from "react-redux";

import { Modal, Button, Form } from "semantic-ui-react";
import {
  createCustomFlag,
  deleteCustomFlag,
  updateCustomFlag,
} from "../../../../redux/actions/customFlagActions";
import { showNotification } from "../../../Notifications";
import { CustomFlagPropType } from "../../../propTypes";

class CustomFlagForm extends React.Component {
  static propTypes = {
    open: PropTypes.bool,
    flag: CustomFlagPropType,
    onCreate: PropTypes.func.isRequired,
    onUpdate: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
  };

  static defaultProps = {
    open: false,
    flag: null,
  };

  formElement = React.createRef();

  constructor(props) {
    super(props);

    this.state = {
      isSaving: false,
      flagData: {},
      errors: null,
    };
  }

  createFlag() {
    const { onCreate, onSave } = this.props;
    const { flagData } = this.state;

    this.setState({ isSaving: true });
    onCreate({ key: null, label: null, shortcut: null, ...flagData }).then(
      () => {
        showNotification({ title: "Success", message: "Custom flag created", status: "success" });
        this.resetForm();
        return onSave(null, flagData.key);
      },
      error => {
        this.setState({ isSaving: false, errors: error.data });
      }
    );
  }

  updateFlag() {
    const { onUpdate, onSave, flag } = this.props;
    const { flagData } = this.state;

    this.setState({ isSaving: true });
    onUpdate({ ...flag, ...flagData }).then(
      () => {
        showNotification({ title: "Success", message: "Custom flag updated", status: "success" });
        this.resetForm();
        return onSave(flag.key, flagData.key);
      },
      error => {
        this.setState({ isSaving: false, errors: error.data });
      }
    );
  }

  deleteFlag() {
    const { onDelete, onSave, flag } = this.props;

    // eslint-disable-next-line no-alert,no-restricted-globals
    const proceed = confirm("Are you sure you want to continue? This action is not reversible.");
    if (!proceed) return;

    this.setState({ isSaving: true });
    onDelete(flag).then(
      () => {
        showNotification({ title: "Success", message: "Custom flag deleted", status: "success" });
        this.resetForm();
        return onSave(flag.key, null);
      },
      error => {
        showNotification({ title: "Error", message: "Unable to delete flag", status: "error" });
        this.setState({ isSaving: false, errors: error.data });
      }
    );
  }

  cancel() {
    const { onCancel } = this.props;

    this.resetForm();
    return onCancel();
  }

  resetForm() {
    this.setState({ isSaving: false, flagData: {}, errors: null });
  }

  renderCreateForm() {
    const { isSaving } = this.state;

    return (
      <React.Fragment>
        <Modal.Header>Create Custom Flag</Modal.Header>
        <Modal.Content>
          <Form id="create-custom-flag-form">{this.renderFormFields()}</Form>
        </Modal.Content>
        <Modal.Actions>
          <Button
            color="green"
            onClick={() => this.createFlag()}
            disabled={isSaving}
            loading={isSaving}
          >
            Create
          </Button>
        </Modal.Actions>
      </React.Fragment>
    );
  }

  renderUpdateForm() {
    const { isSaving } = this.state;

    return (
      <React.Fragment>
        <Modal.Header>Update Custom Flag</Modal.Header>
        <Modal.Content>
          <Form id="update-custom-flag-form">{this.renderFormFields()}</Form>
        </Modal.Content>
        <Modal.Actions>
          <Button
            color="red"
            onClick={() => this.deleteFlag()}
            disabled={isSaving}
            loading={isSaving}
          >
            Delete
          </Button>
          <Button
            color="green"
            onClick={() => this.updateFlag()}
            disabled={isSaving}
            loading={isSaving}
          >
            Save
          </Button>
        </Modal.Actions>
      </React.Fragment>
    );
  }

  renderFormFields(action = "create") {
    const { flag } = this.props;
    const { flagData, errors } = this.state;
    const { key, label, shortcut } = flagData;

    return (
      <React.Fragment>
        <Form.Field>
          <Form.Input
            id={`form-input-${action}-custom-flag-key`}
            help="Hello world"
            label="Unique Identifier"
            placeholder="flag_lower_snake_case"
            value={key == null ? flag?.key : key}
            onChange={e => this.setState({ flagData: { ...flagData, key: e.target.value } })}
            error={
              errors?.key
                ? {
                    content: errors.key.join(" "),
                    pointing: "below",
                  }
                : false
            }
          />
          <Form.Input
            id={`form-input-${action}-custom-flag-label`}
            label="Flag Label"
            placeholder="A brief descriptive label"
            value={label == null ? flag?.label : label}
            onChange={e => this.setState({ flagData: { ...flagData, label: e.target.value } })}
            error={
              errors?.label
                ? {
                    content: errors.label.join(" "),
                    pointing: "below",
                  }
                : false
            }
          />
          <Form.Input
            id={`form-input-${action}-custom-flag-shortcut`}
            label="Keyboard Shortcut"
            placeholder="Two upper-case letters"
            value={shortcut == null ? flag?.shortcut : shortcut}
            onChange={e => this.setState({ flagData: { ...flagData, shortcut: e.target.value } })}
            error={
              errors?.shortcut
                ? {
                    content: errors.shortcut.join(" "),
                    pointing: "below",
                  }
                : false
            }
          />
        </Form.Field>
      </React.Fragment>
    );
  }

  render() {
    const { open, flag } = this.props;
    const contents = flag?.id ? this.renderUpdateForm() : this.renderCreateForm();

    return (
      <Modal open={open} closeIcon onClose={() => this.cancel()}>
        {contents}
      </Modal>
    );
  }
}

const ConnectedCustomFlagForm = connect(
  state => state,
  dispatch => ({
    onCreate: flag => dispatch(createCustomFlag(flag)),
    onUpdate: flag => dispatch(updateCustomFlag(flag)),
    onDelete: flag => dispatch(deleteCustomFlag(flag)),
  })
)(CustomFlagForm);

export default ConnectedCustomFlagForm;
