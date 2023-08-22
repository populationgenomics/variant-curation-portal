import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import { FLAGS } from "../../constants/flags";
import { getCustomFlags } from "../../redux/selectors/customFlagSelectors";
import { CurationResultPropType, CustomFlagPropType } from "../propTypes";

const Flags = ({ result, customFlags }) => (
  <span style={{ fontFamily: "monospace" }}>
    {FLAGS.map((flag) => (result[flag.key] ? flag.shortcut || "" : "")).join(" ")}
    {customFlags
      .map((flag) => (result.custom_flags[flag.key] ? flag.shortcut || "" : ""))
      .join(" ")}
  </span>
);

Flags.propTypes = {
  result: CurationResultPropType.isRequired,
  customFlags: PropTypes.arrayOf(CustomFlagPropType),
};

Flags.defaultProps = { customFlags: [] };

const ConnectedFlags = connect((state) => ({
  customFlags: getCustomFlags(state),
}))(Flags);

export default ConnectedFlags;
