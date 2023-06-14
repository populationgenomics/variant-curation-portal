import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { Header, List } from "semantic-ui-react";

import { FLAG_CODES, FLAG_LABELS } from "../../../../constants/flags";
import verdicts, {
  verdictColors,
  verdictLabels,
  verdictSymbols,
} from "../../../../constants/verdicts";
import { getCustomFlags } from "../../../../redux/selectors/customFlagSelectors";
import { CustomFlagPropType } from "../../../propTypes";

class Legend extends React.PureComponent {
  static propTypes = {
    customFlags: PropTypes.arrayOf(CustomFlagPropType),
  };

  static defaultProps = { customFlags: [] };

  render() {
    const { customFlags } = this.props;

    return (
      <List relaxed>
        <Header>Technical Flags</Header>
        <List.Item>
          <List horizontal>
            {["flag_no_read_data", "flag_reference_error"].map(flag => (
              <List.Item key={flag}>
                {FLAG_CODES[flag]} = {FLAG_LABELS[flag]}
              </List.Item>
            ))}
          </List>
        </List.Item>
        <div style={{ marginLeft: "1rem" }}>
          <Header sub style={{ marginTop: "0.5rem" }}>
            Mapping Error Flags
          </Header>
          <List.Item>
            <List horizontal>
              {["flag_self_chain", "flag_str_or_low_complexity", "flag_low_umap_m50"].map(flag => (
                <List.Item key={flag}>
                  {FLAG_CODES[flag]} = {FLAG_LABELS[flag]}
                </List.Item>
              ))}
            </List>
          </List.Item>
          <div style={{ marginLeft: "1rem" }}>
            <Header sub style={{ marginTop: "0.5rem" }}>
              Dubious Read Alignment Flags
            </Header>
            <List.Item>
              <List horizontal>
                {[
                  "flag_mismapped_read",
                  "flag_complex_event",
                  "flag_stutter",
                  "flag_repetitive_sequence",
                  "flag_dubious_other",
                ].map(flag => (
                  <List.Item key={flag}>
                    {FLAG_CODES[flag]} = {FLAG_LABELS[flag]}
                  </List.Item>
                ))}
              </List>
            </List.Item>
          </div>
          <Header sub style={{ marginTop: "0.5rem" }}>
            Genotyping Error Flags
          </Header>
          <List.Item>
            <List horizontal>
              {[
                "flag_low_genotype_quality",
                "flag_low_read_depth",
                "flag_allele_balance",
                "flag_gc_rich",
                "flag_homopolymer_or_str",
                "flag_strand_bias",
              ].map(flag => (
                <List.Item key={flag}>
                  {FLAG_CODES[flag]} = {FLAG_LABELS[flag]}
                </List.Item>
              ))}
            </List>
          </List.Item>
        </div>

        <Header style={{ marginTop: "0.5rem" }}>Impact Flags</Header>
        <div style={{ marginLeft: "1rem" }}>
          <Header sub style={{ marginTop: "0.5rem" }}>
            Inconsequential Transcript Flags
          </Header>
          <List.Item>
            <List horizontal>
              {[
                "flag_multiple_annotations",
                "flag_pext_less_than_half_max",
                "flag_uninformative_pext",
                "flag_minority_of_transcripts",
                "flag_minor_protein_isoform",
                "flag_weak_exon_conservation",
                "flag_untranslated_transcript",
              ].map(flag => (
                <List.Item key={flag}>
                  {FLAG_CODES[flag]} = {FLAG_LABELS[flag]}
                </List.Item>
              ))}
            </List>
          </List.Item>
          <Header sub style={{ marginTop: "0.5rem" }}>
            Rescue Flags
          </Header>
          <List.Item>
            <List horizontal>
              {[
                "flag_mnp",
                "flag_frame_restoring_indel",
                "flag_first_150_bp",
                "flag_in_frame_sai",
                "flag_methionine_resuce",
                "flag_escapes_nmd",
                "flag_low_truncated",
              ].map(flag => (
                <List.Item key={flag}>
                  {FLAG_CODES[flag]} = {FLAG_LABELS[flag]}
                </List.Item>
              ))}
            </List>
          </List.Item>
        </div>

        <Header style={{ marginTop: "0.5rem" }}>Comment Flags</Header>
        <List.Item>
          <List horizontal>
            {[
              "flag_complex_splicing",
              "flag_complex_other",
              "flag_flow_chart_overridden",
              "flag_second_opinion_required",
              "flag_sanger_confirmation_recommended",
            ].map(flag => (
              <List.Item key={flag}>
                {FLAG_CODES[flag]} = {FLAG_LABELS[flag]}
              </List.Item>
            ))}
          </List>
        </List.Item>

        {customFlags.length ? (
          <>
            <Header style={{ marginTop: "0.5rem" }}>Custom Flags</Header>
            <List.Item>
              <List horizontal>
                {customFlags.map(flag => (
                  <List.Item key={flag.key}>
                    {flag.shortcut} = {flag.label}
                  </List.Item>
                ))}
              </List>
            </List.Item>
          </>
        ) : null}

        <Header sub style={{ marginTop: "0.5rem" }}>
          Verdict
        </Header>
        <List.Item>
          <List horizontal>
            {verdicts.map(verdict => (
              <List.Item key={verdict}>
                <span style={{ color: verdictColors[verdict] }}>
                  {verdictSymbols[verdict]} {verdictLabels[verdict]}
                </span>
              </List.Item>
            ))}
          </List>
        </List.Item>
      </List>
    );
  }
}

const ConnectedLegend = connect(state => ({
  customFlags: getCustomFlags(state),
}))(Legend);

export default ConnectedLegend;
