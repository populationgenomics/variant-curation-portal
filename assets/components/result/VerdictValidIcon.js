import React from "react";

import { Icon, Popup } from "semantic-ui-react";
import { connect } from "react-redux";
import { CurationResultPropType } from "../propTypes";
import { getCurationResult } from "../../redux/selectors/curationResultSelectors";
import { CurationResultVerdictValidator } from "../../utilities/CurationFlagRules";

const VerdictValidIcon = ({ result }) => {
  const validator = new CurationResultVerdictValidator();

  if (validator.isValid(result)) return null;

  return (
    <Popup
      content={<p>Verdict is not compatible with the current flag selection.</p>}
      trigger={<Icon name="exclamation triangle" color="red" />}
    />
  );
};

VerdictValidIcon.propTypes = {
  result: CurationResultPropType.isRequired,
};

const ConnectedVerdictValidIcon = connect((state) => ({
  result: getCurationResult(state),
}))(VerdictValidIcon);

export default ConnectedVerdictValidIcon;
