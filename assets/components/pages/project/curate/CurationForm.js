import PropTypes from "prop-types";
import React from "react";
import { connect } from "react-redux";
import {
  Button,
  Checkbox,
  Divider,
  Form,
  Header,
  Message,
  Radio,
  Ref,
  TextArea,
} from "semantic-ui-react";

import { FLAG_LABELS, FLAG_SHORTCUTS } from "../../../../constants/flags";
import verdicts, { verdictLabels } from "../../../../constants/verdicts";
import { saveResult, setResult } from "../../../../redux/actions/curationResultActions";
import {
  getCurationResult,
  getCurationResultErrors,
} from "../../../../redux/selectors/curationResultSelectors";
import { showNotification } from "../../../Notifications";
import { CurationResultPropType } from "../../../propTypes";
import KeyboardShortcut, { KeyboardShortcutHint } from "../../../KeyboardShortcut";

class CurationForm extends React.Component {
  static propTypes = {
    value: CurationResultPropType.isRequired,
    errors: PropTypes.object, // eslint-disable-line react/forbid-prop-types
    onChange: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
  };

  static defaultProps = {
    errors: null,
  };

  formElement = React.createRef();

  constructor(props) {
    super(props);

    this.syncedFields = {
      flag_dubious_read_alignment: [
        "flag_mismapped_read",
        "flag_complex_event",
        "flag_stutter",
        "flag_dubious_str_or_low_complexity",
        "flag_dubious_other",
      ],
    };

    this.state = {
      isSaving: false,
    };
  }

  setResultField(field, fieldValue) {
    const { value, onChange } = this.props;
    onChange(this.syncFields({ ...value, [field]: fieldValue }));
  }

  toggleResultField(field) {
    const { value, onChange } = this.props;
    onChange(this.syncFields({ ...value, [field]: !value[field] }));
  }

  saveResult() {
    const { value, onSubmit } = this.props;

    this.setState({ isSaving: true });
    onSubmit(value).then(
      () => {
        showNotification({ title: "Success", message: "Curation saved", status: "success" });
        this.setState({ isSaving: false });
      },
      () => {
        showNotification({ title: "Error", message: "Unable to save curation", status: "error" });
        this.setState({ isSaving: false });
      }
    );
  }

  syncFields(result) {
    const newResult = { ...result };

    Object.entries(this.syncedFields).forEach(([field, children]) => {
      newResult[field] = children.reduce((acc, f) => acc || newResult[f], false);
    });

    return newResult;
  }

  renderFlagInput(field, label, shortcut, parent = false) {
    const { value } = this.props;

    const disabledFields = Object.keys(this.syncedFields);

    return (
      <React.Fragment key={field}>
        <Form.Field
          checked={value[field]}
          className="mousetrap"
          control={Checkbox}
          id={field}
          label={{
            children: (
              <React.Fragment>
                {parent ? <Header sub>{label}</Header> : label}
                {shortcut != null ? <KeyboardShortcutHint keys={shortcut} /> : null}
              </React.Fragment>
            ),
          }}
          onChange={e => {
            return disabledFields.includes(field)
              ? null
              : this.setResultField(field, e.target.checked);
          }}
        />
        {shortcut != null ? (
          <KeyboardShortcut
            keys={shortcut}
            onShortcut={() => {
              return disabledFields.includes(field) ? null : this.toggleResultField(field);
            }}
          />
        ) : null}
      </React.Fragment>
    );
  }

  render() {
    const { value, errors } = this.props;
    const { isSaving } = this.state;

    return (
      <Ref innerRef={this.formElement}>
        <Form
          id="curationForm"
          onSubmit={e => {
            e.preventDefault();
            this.saveResult();
          }}
          error={Boolean(errors)}
        >
          <Form.Field
            control={TextArea}
            id="notes"
            label={{
              children: (
                <React.Fragment>
                  Notes
                  <KeyboardShortcutHint keys="n o" />
                </React.Fragment>
              ),
            }}
            value={value.notes}
            onChange={e => {
              this.setResultField("notes", e.target.value);
            }}
          />
          <KeyboardShortcut
            keys="n o"
            onShortcut={e => {
              document.getElementById("notes").focus();
              e.preventDefault(); // Prevent shortcut from being typed into textarea
            }}
          />
          <div style={{ columns: 2 }}>
            {/* Render Technical Flags */}
            <Header sub style={{ marginBottom: "0.5rem" }}>
              Technical
            </Header>
            {["flag_no_read_data", "flag_reference_error"].map(flag =>
              this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag])
            )}
            {/* Render Mapping Error Flags */}
            {["flag_mapping_error"].map(flag =>
              this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag], true)
            )}
            <div style={{ marginLeft: "1rem", marginBottom: "1rem" }}>
              {["flag_self_chain", "flag_str_or_low_complexity", "flag_low_umap_m50"].map(flag =>
                this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag])
              )}
              {/* Render Dubious Read Alignment Flags */}
              {["flag_dubious_read_alignment"].map(flag =>
                this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag], true)
              )}
              <div style={{ marginLeft: "2rem" }}>
                {[
                  "flag_mismapped_read",
                  "flag_complex_event",
                  "flag_stutter",
                  "flag_dubious_str_or_low_complexity",
                  "flag_dubious_other",
                ].map(flag => this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag]))}
              </div>
            </div>
            {/* Render Genotyping Error Flags */}
            {["flag_genotyping_error"].map(flag =>
              this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag], true)
            )}
            <div style={{ marginLeft: "1rem", marginBottom: "1rem" }}>
              {[
                "flag_low_genotype_quality",
                "flag_low_read_depth",
                "flag_allele_balance",
                "flag_gc_rich",
                "flag_homopolymer_or_str",
                "flag_strand_bias",
              ].map(flag => this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag]))}
            </div>
            {/* Render Impact Flags */}
            <Header sub style={{ marginBottom: "0.5rem" }}>
              Impact
            </Header>
            {/* Render Inconsequential Transcript Flags */}
            {["flag_inconsequential_transcript"].map(flag =>
              this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag], true)
            )}
            <div style={{ marginLeft: "1rem", marginBottom: "1rem" }}>
              {[
                "flag_multiple_annotations",
                "flag_pext_less_than_half_max",
                "flag_uninformative_pext",
                "flag_minority_of_transcripts",
                "flag_weak_exon_conservation",
                "flag_untranslated_transcript",
              ].map(flag => this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag]))}
            </div>
            {/* Render Rescue Flags */}
            {["flag_rescue"].map(flag =>
              this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag], true)
            )}
            <div style={{ marginLeft: "1rem", marginBottom: "1rem" }}>
              {[
                "flag_mnp",
                "flag_frame_restoring_indel",
                "flag_first_150_bp",
                "flag_in_frame_sai",
                "flag_methionine_resuce",
                "flag_escapes_nmd",
                "flag_low_truncated",
              ].map(flag => this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag]))}
            </div>
            {/* Render comment flags */}
            <Header sub style={{ marginBottom: "0.5rem" }}>
              Comments
            </Header>
            {[
              "flag_complex_splicing",
              "flag_complex_other",
              "flag_flow_chart_overridden",
              "flag_second_opinion_required",
            ].map(flag => this.renderFlagInput(flag, FLAG_LABELS[flag], FLAG_SHORTCUTS[flag]))}
          </div>
          <Header sub>Verdict</Header>
          <Form.Group>
            {verdicts.map((verdict, i) => (
              <React.Fragment key={verdict}>
                <Form.Field
                  control={Radio}
                  checked={value.verdict === verdict}
                  label={{
                    children: (
                      <React.Fragment>
                        {verdictLabels[verdict]}
                        <KeyboardShortcutHint keys={`${i + 1}`} />
                      </React.Fragment>
                    ),
                  }}
                  name="verdict"
                  value={verdict}
                  onChange={(e, { value: selectedVerdict }) => {
                    this.setResultField("verdict", selectedVerdict);
                  }}
                />
                <KeyboardShortcut
                  keys={`${i + 1}`}
                  onShortcut={() => {
                    this.setResultField("verdict", verdict);
                  }}
                />
              </React.Fragment>
            ))}
          </Form.Group>
          {errors && errors.verdict && <Message error>{errors.verdict}</Message>}
          <Divider />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>
              <Button
                data-shortcut="s"
                disabled={isSaving}
                loading={isSaving}
                primary
                type="submit"
              >
                Save <KeyboardShortcutHint keys="s" color="rgba(255,255,255,0.8)" />
              </Button>
            </span>
            <KeyboardShortcut
              keys="s"
              onShortcut={() => {
                this.saveResult();
              }}
            />

            {this.renderFlagInput("should_revisit", "Revisit this variant", "r v")}
          </div>
        </Form>
      </Ref>
    );
  }
}

const ConnectedCurationForm = connect(
  state => ({
    errors: getCurationResultErrors(state),
    value: getCurationResult(state),
  }),
  (dispatch, ownProps) => ({
    onChange: result => dispatch(setResult(result)),
    onSubmit: result => dispatch(saveResult(result, ownProps.projectId, ownProps.variantId)),
  })
)(CurationForm);

ConnectedCurationForm.propTypes = {
  projectId: PropTypes.number.isRequired,
  variantId: PropTypes.number.isRequired,
};

export default ConnectedCurationForm;
