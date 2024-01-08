import PropTypes, { arrayOf } from "prop-types";
import React from "react";
import { Button, List } from "semantic-ui-react";

const AnnotationsList = ({ annotations }) => {
  const annotationsGroupedByGene = annotations.reduce(
    (acc, annotation) => ({
      ...acc,
      [annotation.gene_id]: [...(acc[annotation.gene_id] || []), annotation],
    }),
    {}
  );

  return (
    <List>
      {Object.keys(annotationsGroupedByGene).map((geneId) => (
        <List.Item key={geneId}>
          <List.Header>{annotationsGroupedByGene[geneId][0].gene_symbol}</List.Header>
          <List.List>
            {annotationsGroupedByGene[geneId].map((annotation) => (
              <List.Item key={annotation.transcript_id}>
                <List.Content>
                  <List.Header>{annotation.transcript_id}</List.Header>
                  <List.Description>
                    {annotation.consequence}
                    {annotation.loftee && (
                      <React.Fragment>
                        <br />
                        LOFTEE: {annotation.loftee}
                        {annotation.loftee === "LC" && ` (${annotation.loftee_filter})`}
                      </React.Fragment>
                    )}
                    {annotation.loftee_flags && (
                      <React.Fragment>
                        <br />
                        LOFTEE Flags: {annotation.loftee_flags}
                      </React.Fragment>
                    )}
                    {annotation.hgvsp && (
                      <React.Fragment>
                        <br />
                        HGVSP: {annotation.hgvsp}
                      </React.Fragment>
                    )}
                    {annotation.hgvsc && (
                      <React.Fragment>
                        <br />
                        HGVSC: {annotation.hgvsc}
                      </React.Fragment>
                    )}
                    {annotation.appris && (
                      <React.Fragment>
                        <br />
                        appris: {annotation.appris}
                      </React.Fragment>
                    )}
                    {annotation.mane_select && (
                      <React.Fragment>
                        <br />
                        MANE SELECT: {annotation.mane_select}
                      </React.Fragment>
                    )}
                    {annotation.exon && (
                      <React.Fragment>
                        <br />
                        Exon: {annotation.exon}
                      </React.Fragment>
                    )}
                  </List.Description>
                </List.Content>
              </List.Item>
            ))}
          </List.List>
        </List.Item>
      ))}
    </List>
  );
};

AnnotationsList.propTypes = {
  annotations: PropTypes.arrayOf(
    PropTypes.shape({
      consequence: PropTypes.string,
      gene_id: PropTypes.string,
      gene_symbol: PropTypes.string,
      transcript_id: PropTypes.string,
      loftee: PropTypes.string,
      loftee_filter: PropTypes.string,
      loftee_flags: PropTypes.string,
      hgvsp: PropTypes.string,
      hgvsc: PropTypes.string,
      appris: PropTypes.string,
      mane_select: PropTypes.string,
      exon: PropTypes.string,
    })
  ).isRequired,
};

const TagsList = ({ tags }) => (
  <List>
    {tags.map((tag, index) => (
      // eslint-disable-next-line react/no-array-index-key
      <List.Item key={index}>
        <List.Content>
          <List.Header>{tag.label}</List.Header>
          <List.Description>{tag.value}</List.Description>
        </List.Content>
      </List.Item>
    ))}
  </List>
);

TagsList.propTypes = {
  tags: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ).isRequired,
};

class VariantData extends React.Component {
  static propTypes = {
    variant: PropTypes.shape({
      qc_filter: PropTypes.string,
      AC: PropTypes.number,
      AN: PropTypes.number,
      AF: PropTypes.number,
      GT: PropTypes.arrayOf(PropTypes.string),
      DP: PropTypes.arrayOf(PropTypes.number),
      GQ: PropTypes.arrayOf(PropTypes.number),
      AD: PropTypes.arrayOf(arrayOf(PropTypes.number)),
      DP_all: PropTypes.arrayOf(PropTypes.number),
      GQ_all: PropTypes.arrayOf(PropTypes.number),
      AD_all: PropTypes.arrayOf(arrayOf(PropTypes.number)),
      sample_ids: PropTypes.arrayOf(PropTypes.string),
      n_homozygotes: PropTypes.number,
      n_heterozygotes: PropTypes.number,
      annotations: PropTypes.arrayOf(PropTypes.object).isRequired, // eslint-disable-line react/forbid-prop-types
      tags: PropTypes.arrayOf(PropTypes.object).isRequired, // eslint-disable-line react/forbid-prop-types
      reference_genome: PropTypes.oneOf(["GRCh37", "GRCh38"]).isRequired,
      liftover_variant_id: PropTypes.string,
    }).isRequired,
  };

  state = {
    showAll: false,
  };

  render() {
    const { variant } = this.props;
    const { showAll } = this.state;

    return (
      <List>
        <List.Item>
          <strong>Reference genome:</strong> {variant.reference_genome}
        </List.Item>
        {variant.liftover_variant_id && (
          <List.Item>
            <strong>Liftover:</strong> {variant.liftover_variant_id}
          </List.Item>
        )}
        <List.Item>
          <strong>Filter:</strong> {variant.qc_filter}
        </List.Item>
        <List.Item>
          <strong>Callset AF:</strong> {variant.AF}
        </List.Item>
        <List.Item>
          <strong>Callset AC:</strong> {variant.AC}
        </List.Item>
        <List.Item>
          <strong>Callset AN:</strong> {variant.AN}
        </List.Item>
        <List.Item>
          <strong>Sample IDs:</strong> {(variant.sample_ids ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Genotype Call:</strong> {(variant.GT ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Read Depth:</strong> {(variant.DP ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Genotype Quality:</strong> {(variant.GQ ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Allelic Depths:</strong> {(variant.AD ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Read Depth (all ALT genotypes):</strong> {(variant.DP_all ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Genotype Quality (all ALT genotypes):</strong> {(variant.GQ_all ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Allelic Depth (all ALT genotypes):</strong> {(variant.AD_all ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Number of homozygotes:</strong> {variant.n_homozygotes}
        </List.Item>
        <List.Item>
          <strong>Number of heterozygotes:</strong> {variant.n_heterozygotes}
        </List.Item>
        <List.Item>
          <strong>Annotations:</strong>
          {variant.annotations.length > 0 ? (
            <>
              <AnnotationsList
                annotations={variant.annotations
                  .sort((a, b) => {
                    if (a.mane_select === b.mane_select) {
                      return 0;
                    }
                    if (a.mane_select === null) {
                      return 1;
                    }
                    if (b.mane_select === null) {
                      return -1;
                    }
                    return a < b ? 1 : -1;
                  })
                  .slice(0, showAll ? variant.annotations.length : 1)}
              />
              {variant.annotations.length > 1 && (
                <Button
                  basic
                  size="small"
                  onClick={() => {
                    this.setState((state) => ({ ...state, showAll: !state.showAll }));
                  }}
                >
                  {showAll ? "Show MANE" : "Show All"}
                </Button>
              )}
            </>
          ) : (
            <p>No annotations available for this variant</p>
          )}
        </List.Item>
        <List.Item>
          <strong>Tags:</strong>
          {variant.tags.length > 0 ? (
            <TagsList tags={variant.tags} />
          ) : (
            <p>No tags available for this variant</p>
          )}
        </List.Item>
      </List>
    );
  }
}

export default VariantData;
