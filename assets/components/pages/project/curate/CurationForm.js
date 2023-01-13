import React from "react";
import PropTypes from "prop-types";
import { omit, sortBy } from "lodash";
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
import { getCustomFlags } from "../../../../redux/selectors/customFlagSelectors";
import { showNotification } from "../../../Notifications";
import { CurationResultPropType, CustomFlagPropType } from "../../../propTypes";
import KeyboardShortcut, { KeyboardShortcutHint } from "../../../KeyboardShortcut";
import CustomFlagForm from "./CustomFlagForm";

class CurationForm extends React.Component {
  static propTypes = {
    value: CurationResultPropType.isRequired,
    errors: PropTypes.object, // eslint-disable-line react/forbid-prop-types
    customFlags: PropTypes.arrayOf(CustomFlagPropType),
    onChange: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
  };

  static defaultProps = {
    errors: null,
    customFlags: [],
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
      showCreateFlagForm: false,
      flagToUpdate: null,
    };
  }

  setResultField(field, fieldValue) {
    const { value, onChange } = this.props;
    onChange(this.syncFields({ ...value, [field]: fieldValue }));
  }

  setCustomFlagField(field, fieldValue) {
    const { value, onChange } = this.props;
    const customFlags = value.custom_flags;
    onChange({ ...value, custom_flags: { ...customFlags, [field]: fieldValue } });
  }

  updateCustomFlagField(oldField, newField) {
    const { value, onChange } = this.props;
    const customFlags = { ...(value.custom_flags || {}) };

    // Adding a new custom flag
    if (oldField == null && newField != null) {
      onChange({
        ...value,
        custom_flags: { ...customFlags, [newField]: false },
      });
    }

    // Deleting an existing field
    if (oldField != null && newField == null) {
      onChange({
        ...value,
        custom_flags: { ...omit(customFlags, oldField) },
      });
    }

    // Updating an existing custom flag
    if (oldField != null && newField != null) {
      const fieldValue = customFlags[oldField];
      onChange({
        ...value,
        custom_flags: { ...omit(customFlags, oldField), [newField]: fieldValue },
      });
    }
  }

  toggleResultField(field) {
    const { value, onChange } = this.props;
    onChange(this.syncFields({ ...value, [field]: !value[field] }));
  }

  toggleCustomFlagField(field) {
    const { value, onChange } = this.props;
    const customFlags = value.custom_flags;
    onChange({ ...value, custom_flags: { ...customFlags, [field]: !customFlags[field] } });
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

  renderFlagInput(field, label, shortcut, parent = false, isCustomFlag = false) {
    const { value, customFlags } = this.props;

    const disabledFields = Object.keys(this.syncedFields);

    return (
      <React.Fragment key={field}>
        <Form.Field
          checked={isCustomFlag ? value.custom_flags[field] : value[field]}
          className="mousetrap"
          control={Checkbox}
          id={field}
          label={{
            children: (
              <React.Fragment>
                {parent ? <Header sub>{label}</Header> : label}
                {shortcut != null ? <KeyboardShortcutHint keys={shortcut} /> : null}
                {isCustomFlag ? (
                  <Button
                    onClick={e => {
                      e.preventDefault();
                      this.setState({ flagToUpdate: customFlags.find(f => f.key === field) });
                    }}
                    style={{
                      borderColor: "rgba(0,0,0,0.55)",
                      borderStyle: "solid",
                      borderWidth: "1px",
                      borderRadius: "5px",
                      padding: "1px 4px 2px",
                      marginLeft: "0.5em",
                      color: "rgba(0,0,0,0.55)",
                      fontSize: "0.8em",
                    }}
                  >
                    edit
                  </Button>
                ) : null}
              </React.Fragment>
            ),
          }}
          onChange={e => {
            if (disabledFields.includes(field)) return null;
            if (isCustomFlag) return this.setCustomFlagField(field, e.target.checked);
            return this.setResultField(field, e.target.checked);
          }}
        />
        {shortcut != null ? (
          <KeyboardShortcut
            keys={shortcut}
            onShortcut={() => {
              if (disabledFields.includes(field)) return null;
              if (isCustomFlag) return this.toggleCustomFlagField(field);
              return this.toggleResultField(field);
            }}
          />
        ) : null}
      </React.Fragment>
    );
  }

  renderCustomFlags = () => {
    const { customFlags } = this.props;

    let customFlagContent = <p>There are no custom flags</p>;
    if (customFlags?.length) {
      customFlagContent = sortBy(customFlags, ["key"]).map(flag =>
        this.renderFlagInput(
          flag.key,
          flag.label,
          flag.shortcut
            .toLowerCase()
            .split("")
            .join(" "),
          false,
          true
        )
      );
    }

    return (
      <>
        <div style={{ marginBottom: 8 }}>
          <Header sub style={{ display: "inline" }}>
            Custom Flags
          </Header>
          <Button
            onClick={e => {
              e.preventDefault();
              this.setState({ showCreateFlagForm: true });
            }}
            style={{
              borderColor: "rgba(0,0,0,0.55)",
              borderStyle: "solid",
              borderWidth: "1px",
              borderRadius: "5px",
              padding: "1px 4px 2px",
              marginLeft: "0.5em",
              color: "rgba(0,0,0,0.55)",
              fontSize: "0.8em",
            }}
          >
            +
          </Button>
        </div>
        <div style={{ columns: 2 }}>{customFlagContent}</div>
      </>
    );
  };

  render() {
    const { value, errors } = this.props;
    const { isSaving, flagToUpdate, showCreateFlagForm } = this.state;

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

          {this.renderCustomFlags()}
          <CustomFlagForm
            open={flagToUpdate !== null || showCreateFlagForm}
            flag={flagToUpdate}
            onSave={(oldKey, newKey) => {
              this.setState({ flagToUpdate: null, showCreateFlagForm: false });
              this.updateCustomFlagField(oldKey, newKey);
            }}
            onCancel={() => {
              this.setState({ flagToUpdate: null, showCreateFlagForm: false });
            }}
          />

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
    customFlags: getCustomFlags(state),
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
