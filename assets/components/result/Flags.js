import React from "react";

import { FLAGS } from "../../constants/flags";
import { CurationResultPropType } from "../propTypes";

const Flags = ({ result }) => (
  <span style={{ fontFamily: "monospace" }}>
    {FLAGS.map(flag => (result[flag.key] ? flag.shortcut || "" : "")).join(" ")}
  </span>
);

Flags.propTypes = {
  result: CurationResultPropType.isRequired,
};

export default Flags;
