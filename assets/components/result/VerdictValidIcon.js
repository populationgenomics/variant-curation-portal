import React from "react";

import { Icon, Popup } from "semantic-ui-react";
import { CurationResultPropType } from "../propTypes";
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

export default VerdictValidIcon;
