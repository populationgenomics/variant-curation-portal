import PropTypes from "prop-types";
import React from "react";
import { Message } from "semantic-ui-react";

// Access control is actually enforced server side.
// This is used for cases where a user navigates to a page
// that would require other permissions to use.

export const can = (user, action, resourceType, resource) => {
  if (!user) {
    return false;
  }

  switch (resourceType) {
    case "project":
      switch (action) {
        case "add":
          return user.permissions.includes("add_project");
        case "edit":
          return Boolean(resource.owners) && resource.owners.includes(user.username);
        case "add_variant_to_project":
          return can(user, "edit", "project", resource) && user.permissions.includes("add_variant");
        default:
          throw new Error(`Unknown action "${action}" for resource type "${resourceType}`);
      }
    default:
      throw new Error(`Unknown resource type "${resourceType}"`);
  }
};

// eslint-disable-next-line react/prop-types
export const PermissionRequired = ({ action, children, resource, resourceType, user }) => {
  if (!can(user, action, resourceType, resource)) {
    return (
      <Message error>
        <Message.Header>Access Denied</Message.Header>
        <p>You do not have permission to view this content.</p>
      </Message>
    );
  }

  return children;
};

PermissionRequired.propTypes = {
  action: PropTypes.string.isRequired,
  resource: PropTypes.any, // eslint-disable-line react/forbid-prop-types
  resourceType: PropTypes.string.isRequired,
  user: PropTypes.shape({
    username: PropTypes.string.isRequired,
    permissions: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
};

PermissionRequired.defaultProps = {
  resource: undefined,
  user: null,
};
