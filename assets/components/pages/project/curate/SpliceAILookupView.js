import PropTypes from "prop-types";
import React from "react";
import { Header, Segment } from "semantic-ui-react";

const SpliceAILookupView = ({ variant, scoreType, maxDistance, usePrecomputed }) => {
  console.log(variant);
  const spliceAiVariantId = variant.variant_id;
  // Remove "GRCh" characters
  const referenceGenome = variant.reference_genome.replace("GRCh", "");

  if (!spliceAiVariantId) {
    return (
      <Segment placeholder textAlign="center">
        <Header>
          SpliceAI lookup page unavailable for this variant
          <br />
          No variant ID
        </Header>
      </Segment>
    );
  }

  const url = `https://spliceailookup.broadinstitute.org/#variant=${spliceAiVariantId}&hg=${referenceGenome}&distance=${maxDistance}&mask=${
    scoreType === "masked" ? 1 : 0
  }&precomputed=${usePrecomputed ? 1 : 0}`;

  if (process.env.NODE_ENV === "development") {
    return (
      <Segment id="splice-ai-lookup" placeholder textAlign="center">
        <p>SpliceAI lookup page</p>
        <a href={url}>{url}</a>
      </Segment>
    );
  }

  return (
    <iframe
      title="SpliceAI lookup page"
      id="splice-ai-lookup"
      src={url}
      style={{ width: "100%", height: "3900px" }}
    />
  );
};

SpliceAILookupView.propTypes = {
  variant: PropTypes.shape({
    reference_genome: PropTypes.oneOf(["GRCh37", "GRCh38"]).isRequired,
    variant_id: PropTypes.string.isRequired,
    liftover_variant_id: PropTypes.string,
  }).isRequired,
  scoreType: PropTypes.oneOf(["masked", "raw"]),
  maxDistance: PropTypes.number,
  usePrecomputed: PropTypes.bool,
};

SpliceAILookupView.defaultProps = {
  scoreType: "raw",
  maxDistance: 500,
  usePrecomputed: false,
};

export default SpliceAILookupView;
