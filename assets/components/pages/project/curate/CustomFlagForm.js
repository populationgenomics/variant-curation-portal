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

  // eslint-disable-next-line react/no-unused-class-component-methods
  formElement = React.createRef();

  constructor(props) {
    super(props);

    const { flag } = this.props;

    this.state = {
      isSaving: false,
      flagData: { key: "", label: "", shortcut: "", ...(flag || {}) },
      errors: null,
    };
  }

  componentWillUnmount() {
    this.resetForm();
  }

  createFlag() {
    const { onCreate, onSave } = this.props;
    const { flagData } = this.state;

    this.setState({ isSaving: true });
    onCreate({ key: null, label: null, shortcut: null, ...flagData }).then(
      () => {
        showNotification({ title: "Success", message: "Custom flag created", status: "success" });
        return onSave(null, flagData.key);
      },
      (error) => {
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
        return onSave(flag.key, flagData.key);
      },
      (error) => {
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
        return onSave(flag.key, null);
      },
      (error) => {
        showNotification({ title: "Error", message: "Unable to delete flag", status: "error" });
        this.setState({ isSaving: false, errors: error.data });
      }
    );
  }

  cancel() {
    const { onCancel } = this.props;
    return onCancel();
  }

  resetForm() {
    const { flag } = this.props;

    this.setState({
      isSaving: false,
      flagData: { key: "", label: "", shortcut: "", ...flag },
      errors: null,
    });
  }

  renderCreateForm() {
    const { isSaving } = this.state;

    return (
      <React.Fragment>
        <Modal.Header>Add Custom Flag</Modal.Header>

        <Modal.Content>
          <p>
            Create a new custom flag. Note that this flag will be added to all existing and future
            curation results, and be visible to all curators.
          </p>
          <Form id="create-custom-flag-form">{this.renderFormFields()}</Form>
        </Modal.Content>
        <Modal.Actions>
          <Button
            color="green"
            disabled={isSaving}
            loading={isSaving}
            onClick={() => this.createFlag()}
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
        <Modal.Header>Edit Custom Flag</Modal.Header>
        <Modal.Content>
          <p>
            Delete this flag, or edit this flag&apos;s unique identifier, label or shortcut. Note
            that this will update the flag in all existing curation results, for all curators.
            Similarly, deleting this flag will remove it from all existing curation results, for all
            curators.
          </p>
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
    const { flagData, errors } = this.state;

    return (
      <Form.Field>
        <Form.Input
          id={`form-input-${action}-custom-flag-key`}
          name="key"
          help="Hello world"
          label="Unique Identifier"
          placeholder="flag_lower_snake_case"
          value={flagData.key}
          onChange={(e) => this.setState({ flagData: { ...flagData, key: e.target.value } })}
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
          name="label"
          label="Flag Label"
          placeholder="A brief descriptive label"
          value={flagData.label}
          onChange={(e) => this.setState({ flagData: { ...flagData, label: e.target.value } })}
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
          name="shortcut"
          label="Keyboard Shortcut"
          placeholder="Two upper-case letters"
          value={flagData.shortcut}
          onChange={(e) => this.setState({ flagData: { ...flagData, shortcut: e.target.value } })}
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
  (state) => state,
  (dispatch) => ({
    onCreate: (flag) => dispatch(createCustomFlag(flag)),
    onUpdate: (flag) => dispatch(updateCustomFlag(flag)),
    onDelete: (flag) => dispatch(deleteCustomFlag(flag)),
  })
)(CustomFlagForm);

export default ConnectedCustomFlagForm;
