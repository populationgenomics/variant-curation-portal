import PropTypes from "prop-types";
import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, Form, Header, Icon, Message, Modal, Segment } from "semantic-ui-react";

import api from "../../../../api";
import { PermissionRequired } from "../../../../permissions";
import resultsSchema from "../../../../results-schema.json";
import DocumentTitle from "../../../DocumentTitle";
import SchemaDescription from "../../../SchemaDescription";
import Page from "../../Page";

class ImportResultsPage extends Component {
  static propTypes = {
    history: PropTypes.shape({
      push: PropTypes.func.isRequired,
    }).isRequired,
    project: PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
    }).isRequired,
    refreshProject: PropTypes.func.isRequired,
    user: PropTypes.shape({
      username: PropTypes.string.isRequired,
    }),
  };

  static defaultProps = {
    user: null,
  };

  resultsData = null;

  state = {
    fileName: null,
    fileReadError: null,
    hasFileData: false,
    isReadingFile: false,
    isSchemaModalOpen: false,
    isSaving: false,
    saveError: null,
  };

  onSubmit = () => {
    const { history, project, refreshProject } = this.props;

    this.setState({ isSaving: true, saveError: null });
    api
      .post(`/project/${project.id}/results/`, this.resultsData)
      .then(() => {
        refreshProject();
        history.push(`/project/${project.id}/admin/`);
      })
      .catch((error) => {
        this.setState({ isSaving: false, saveError: error });
      });
  };

  onSelectFile = (file) => {
    this.resultsData = null;

    if (!file) {
      this.setState({
        fileName: null,
        fileReadError: null,
        hasFileData: false,
      });
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        this.resultsData = JSON.parse(e.target.result);
        this.setState({ hasFileData: true, isReadingFile: false });
      } catch (err) {
        this.setState({ fileReadError: "Parse error", isReadingFile: false });
      }
    };
    reader.onerror = () => {
      this.setState({ fileReadError: "Read error", isReadingFile: false });
    };
    this.setState({
      fileName: file.name,
      fileReadError: null,
      hasFileData: false,
      isReadingFile: true,
    });
    reader.readAsText(file);
  };

  renderErrorDetail(detail) {
    return Object.entries(detail).map(([key, value], index) => {
      const { variant_id: variantId, curator } = this.resultsData[index];
      return (
        <li key={`${variantId}-${curator}-${key}`}>
          <b>{key}:</b> {value}
        </li>
      );
    });
  }

  renderError(error) {
    if (!error.data) {
      return <Message error header="Failed to upload results (unknown error)" />;
    }

    const errorList = Array.isArray(error.data) ? error.data : [error.data];

    const items = errorList.map((detail, index) => {
      if (Object.entries(detail).length) {
        const { variant_id: variantId, curator } = this.resultsData[index];
        return (
          <>
            <div key={`list-item-${index + 1}`}>
              <b>Item {index + 1}:</b> Variant: {variantId} | Curator: {curator}
              <ul>{this.renderErrorDetail(detail)}</ul>
            </div>
            <br />
          </>
        );
      }
      return null;
    });

    return (
      <Message error>
        <Message.Header>Failed to upload results</Message.Header>
        <Message.List items={items.filter((i) => i != null)} />
      </Message>
    );
  }

  render() {
    const { project, user } = this.props;
    const {
      fileName,
      fileReadError,
      hasFileData,
      isReadingFile,
      isSaving,
      isSchemaModalOpen,
      saveError,
    } = this.state;

    return (
      <Page>
        <DocumentTitle title={project.name} />
        <Header as="h1" dividing>
          {project.name}
        </Header>
        <div>
          <Link to={`/project/${project.id}/admin/`}>Return to project</Link>
        </div>
        <br />

        <PermissionRequired user={user} action="edit" resourceType="project" resource={project}>
          <Segment attached>
            <Header as="h4">Upload results from file</Header>
            <p>
              Existing results will be updated and marked as edited by you if any of the fields in
              the uploaded file differ from what is in the system. The original data in the system
              will be kept for all optional fields in the JSON schema that are not present in the
              uploaded file.
            </p>
            <p>
              Omit the <b>created_at</b> and <b>updated_at</b> fields to set them as the current
              time when creating new results. These timestamp fields will be ignored when updating
              existing results, and the <b>updated_at</b> field will be set to the current time.
            </p>
            <p>
              The <b>editor</b> field is ignored during upload, but is present in the downloaded
              JSON file for your reference.
            </p>
            <Form error={Boolean(fileReadError || saveError)} onSubmit={this.onSubmit}>
              <Button
                as="label"
                disabled={isReadingFile}
                loading={isReadingFile}
                htmlFor="results-file"
              >
                <Icon name="upload" />
                {fileName || "Select results file"}
                <input
                  disabled={isReadingFile}
                  hidden
                  id="results-file"
                  type="file"
                  onChange={(e) => this.onSelectFile(e.target.files[0])}
                />
              </Button>
              {fileReadError && <Message error header="Failed to read file" />}
              {saveError && this.renderError(saveError)}
              <Button disabled={!hasFileData || isSaving} loading={isSaving} primary type="submit">
                Upload
              </Button>
            </Form>
          </Segment>

          <Message attached>
            <p>
              This should be a JSON file containing an array of objects with the following format.
              The expected file format is also available as a{" "}
              <a href="https://json-schema.org" target="_blank" rel="noopener noreferrer">
                JSON schema
              </a>
              .
            </p>
            <Button
              type="button"
              onClick={(e) => {
                this.setState({ isSchemaModalOpen: true });
                e.preventDefault();
              }}
            >
              View JSON Schema
            </Button>
            <Button as="a" download href="/static/bundles/results-schema.json">
              Download JSON Schema
            </Button>
            <SchemaDescription schema={resultsSchema} />
          </Message>

          <Modal
            open={isSchemaModalOpen}
            onClose={() => {
              this.setState({ isSchemaModalOpen: false });
            }}
          >
            <Header>Results Schema</Header>
            <Modal.Content>
              <pre>{JSON.stringify(resultsSchema, null, 2)}</pre>
            </Modal.Content>
            <Modal.Actions>
              <Button
                onClick={() => {
                  this.setState({ isSchemaModalOpen: false });
                }}
              >
                Ok
              </Button>
            </Modal.Actions>
          </Modal>
        </PermissionRequired>
      </Page>
    );
  }
}

export default ImportResultsPage;
