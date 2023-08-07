import PropTypes from "prop-types";

import verdicts from "../constants/verdicts";

export const CurationResultPropType = PropTypes.shape({
  notes: PropTypes.string,
  curator_comments: PropTypes.string,
  verdict: PropTypes.oneOf(["", ...verdicts]),
});

export const CurationAssignmentPropType = PropTypes.shape({
  result: CurationResultPropType,
  variant: PropTypes.object, // eslint-disable-line react/forbid-prop-types
});

export const CustomFlagPropType = PropTypes.shape({
  id: PropTypes.number.isRequired,
  key: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  shortcut: PropTypes.string.isRequired,
});
