import PropTypes from "prop-types";
import React from "react";
import { Route, Switch } from "react-router-dom";

import Fetch from "../../Fetch";
import PageNotFoundPage from "../PageNotFoundPage";
import withParamsAsProps from "../withParamsAsProps";
import AssignVariantsPage from "./admin/AssignVariantsPage";
import EditProjectPage from "./admin/EditProjectPage";
import EditProjectOwnersPage from "./admin/EditProjectOwnersPage";
import ImportResultsPage from "./admin/ImportResultsPage";
import ProjectAdminPage from "./admin/ProjectAdminPage";
import ProjectResultsPage from "./admin/ProjectResultsPage";
import UploadVariantsPage from "./admin/UploadVariantsPage";
import ProjectAssignmentsPage from "./assignments/ProjectAssignmentsPage";
import CurateVariantPage from "./curate/CurateVariantPage";

const ProjectPage = ({ match, projectId, user }) => (
  <Fetch path={`/project/${projectId}/`}>
    {({ data: project, refresh }) => (
      <Switch>
        <Route
          exact
          path={match.path}
          render={(props) => <ProjectAssignmentsPage {...props} project={project} />}
        />

        <Route
          exact
          path={`${match.path}admin/`}
          render={(props) => <ProjectAdminPage {...props} project={project} user={user} />}
        />

        <Route
          exact
          path={`${match.path}edit/`}
          render={(props) => (
            <EditProjectPage {...props} project={project} refreshProject={refresh} user={user} />
          )}
        />

        <Route
          exact
          path={`${match.path}owners/`}
          render={(props) => (
            <EditProjectOwnersPage
              {...props}
              project={project}
              refreshProject={refresh}
              user={user}
            />
          )}
        />

        <Route
          exact
          path={`${match.path}assign/`}
          render={(props) => (
            <AssignVariantsPage {...props} project={project} user={user} refreshProject={refresh} />
          )}
        />

        <Route
          exact
          path={`${match.path}variants/`}
          render={(props) => (
            <UploadVariantsPage {...props} project={project} refreshProject={refresh} user={user} />
          )}
        />

        <Route
          exact
          path={`${match.path}results/`}
          render={(props) => <ProjectResultsPage {...props} project={project} user={user} />}
        />

        <Route
          exact
          path={`${match.path}results/import/`}
          render={(props) => (
            <ImportResultsPage {...props} project={project} refreshProject={refresh} user={user} />
          )}
        />

        <Route
          exact
          path={`${match.path}variant/:variantId/curate/`}
          render={(props) => <CurateVariantPage {...props} project={project} user={user} />}
        />

        <Route component={PageNotFoundPage} />
      </Switch>
    )}
  </Fetch>
);

ProjectPage.propTypes = {
  match: PropTypes.shape({
    path: PropTypes.string.isRequired,
  }).isRequired,
  projectId: PropTypes.number.isRequired,
  user: PropTypes.shape({
    username: PropTypes.string.isRequired,
  }),
};

ProjectPage.defaultProps = {
  user: null,
};

export default withParamsAsProps(({ projectId }) => ({
  projectId: parseInt(projectId, 10),
}))(ProjectPage);
