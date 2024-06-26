import PropTypes from "prop-types";
import React from "react";
import { Button, List, Tab, TabPane } from "semantic-ui-react";
import { Chart, registerables } from "chart.js";
import { Bar } from "react-chartjs-2";

// Register chart.js plugins to use scale types in charts (e.g. "linear")
Chart.register(...registerables);

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

function getPreparedBinnedData(inputValues, binSize, valuesAreAllelicDepths, max = null) {
  const options = {
    scales: {
      x: {
        type: "linear",
        beginAtZero: true,
        max: max !== null ? max : undefined,
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 14,
          },
          color: "#333",
        },
      },
      y: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 14,
          },
          color: "#333",
          callback: (value) => (Number.isInteger(value) ? value : null),
        },
      },
    },
  };

  if (!inputValues) {
    // Handle the case where values is null
    return { data: { labels: [], datasets: [] }, options };
  }

  // Calculate allele balances = ALT/(REF+ALT) where the input array is [[REF, ALT], [REF, ALT], ...]
  let values = inputValues;
  if (valuesAreAllelicDepths) {
    values = inputValues.map((depths) => {
      const result = (depths[1] / (depths[0] + depths[1])).toFixed(2);
      return Number.isNaN(result) ? [] : result;
    });
  }

  // Calculate the binned frequencies of the array values with a for loop
  const frequencies = {};
  for (let i = 0; i < values.length; i += 1) {
    const bin = Math.floor(values[i] / binSize) * binSize; // Bin values in groups of binSize
    frequencies[bin] = (frequencies[bin] || 0) + 1;
  }

  // Prepare data for the bar chart
  const data = {
    labels: Object.keys(frequencies).map(Number),
    datasets: [
      {
        label: "Frequencies",
        data: Object.values(frequencies),
        backgroundColor: "rgba(75,192,192,0.4)",
        borderColor: "rgba(75,192,192,1)",
        borderWidth: 1,
        hoverBackgroundColor: "rgba(75,192,192,0.7)",
        hoverBorderColor: "rgba(75,192,192,1)",
      },
    ],
  };

  return { data, options };
}

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
      AD: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),
      DP_all: PropTypes.arrayOf(PropTypes.number),
      GQ_all: PropTypes.arrayOf(PropTypes.number),
      AD_all: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),
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

    const { data: gqData, options: gqOptions } = getPreparedBinnedData(
      variant.GQ_all,
      5,
      false,
      100
    );
    const { data: dpData, options: dpOptions } = getPreparedBinnedData(
      variant.DP_all,
      5,
      false,
      null
    );
    const { data: abData, options: abOptions } = getPreparedBinnedData(
      variant.AD_all,
      0.05,
      true,
      1.0
    );

    const tabItems = [
      {
        menuItem: "Genotype Qualities",
        render: () => (
          <TabPane>
            <div style={{ height: "300px", width: "100%" }}>
              <Bar data={gqData} options={gqOptions} />
            </div>
          </TabPane>
        ),
      },
      {
        menuItem: "Read Depths",
        render: () => (
          <TabPane>
            <div style={{ height: "300px", width: "100%" }}>
              <Bar data={dpData} options={dpOptions} />
            </div>
          </TabPane>
        ),
      },
      {
        menuItem: "Allele Balances",
        render: () => (
          <TabPane>
            <div style={{ height: "300px", width: "100%" }}>
              <Bar data={abData} options={abOptions} />
            </div>
          </TabPane>
        ),
      },
    ];

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
          <strong>Allelic Depths:</strong>{" "}
          {(variant.AD ?? []).map((depths) => `(${depths.join(", ")})`).join(", ") || "N/A"}
        </List.Item>
        <List.Item>
          <strong>Read Depths (all ALT genotypes):</strong> {(variant.DP_all ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Genotype Quality (all ALT genotypes):</strong> {(variant.GQ_all ?? []).join(", ")}
        </List.Item>
        <List.Item>
          <strong>Allelic Depths (all ALT genotypes):</strong>{" "}
          {(variant.AD_all ?? []).map((depths) => `(${depths.join(", ")})`).join(", ") || "N/A"}
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
        <List.Item>
          <Tab panes={tabItems} />
        </List.Item>
      </List>
    );
  }
}

export default VariantData;
