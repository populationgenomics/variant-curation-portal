import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import { FLAGS } from "../../constants/flags";
import { getCustomFlags } from "../../redux/selectors/customFlagSelectors";
import { CurationResultPropType, CustomFlagPropType } from "../propTypes";
import CurationFlagRules from "../../utilities/CurationFlagRules";

const Flags = ({ result, customFlags }) => (
  <span style={{ fontFamily: "monospace" }}>
    {FLAGS.map((flag) => (result[flag.key] ? flag.shortcut || "" : "")).join(" ")}
    {customFlags
      .map((flag) => (result.custom_flags[flag.key] ? flag.shortcut || "" : ""))
      .join(" ")}
  </span>
);

export const RenderFlagRulesFollowedIcon = ({ result }) => {
  const FlagsList = FLAGS.map((item) => item.key);
  const expectedFlags = CurationFlagRules(
    Object.fromEntries(
      Object.entries(result).filter(([key, value]) => value && FlagsList.includes(key))
    )
  );
  return expectedFlags[result.verdict] ? (
    <span title="Follows Curation Rules">&#9989;</span>
  ) : (
    <span title="Does Not Follow Curation Rules">&#10060;</span>
  );
};

Flags.propTypes = {
  result: CurationResultPropType.isRequired,
  customFlags: PropTypes.arrayOf(CustomFlagPropType),
};

Flags.defaultProps = { customFlags: [] };

const ConnectedFlags = connect((state) => ({
  customFlags: getCustomFlags(state),
}))(Flags);

export default ConnectedFlags;
