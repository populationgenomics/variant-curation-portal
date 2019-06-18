import PropTypes from "prop-types";
import React from "react";

/**
 * Documentation for linking to the UCSC browser:
 * https://genome.ucsc.edu/FAQ/FAQlink.html
 * https://genome.ucsc.edu/goldenPath/help/customTrack.html#optParams
 */

export const UCSCVariantView = ({ variant }) => {
  const assembly = variant.reference_genome === "GRCh38" ? "hg38" : "hg19";
  return (
    <iframe
      title="UCSC variant view"
      id="ucsc"
      width="100%"
      height="4000px"
      src={`https://genome.ucsc.edu/cgi-bin/hgTracks?db=${assembly}&position=${encodeURIComponent(
        `chr${variant.chrom}:${variant.pos - 25}-${variant.pos + 25}`
      )}&highlight=${encodeURIComponent(
        `${assembly}.chr${variant.chrom}:${variant.pos}-${variant.pos}`
      )}`}
    />
  );
};

UCSCVariantView.propTypes = {
  variant: PropTypes.shape({
    chrom: PropTypes.string.isRequired,
    pos: PropTypes.number.isRequired,
    reference_genome: PropTypes.oneOf(["GRCh37", "GRCh38"]).isRequired,
  }).isRequired,
};

export const UCSCGeneView = ({ variant }) => {
  const annotation = variant.annotations.find(a => a.gene_symbol && a.transcript_id);

  if (!annotation) {
    return null;
  }

  const assembly = variant.reference_genome === "GRCh38" ? "hg38" : "hg19";

  return (
    <iframe
      title="UCSC gene view"
      id="ucsc-gene"
      width="100%"
      height="4000px"
      src={`https://genome.ucsc.edu/cgi-bin/hgTracks?db=${assembly}&position=${
        annotation.gene_symbol
      }&singleSearch=knownCanonical&hgFind.matches=${
        annotation.transcript_id
      }&highlight=${encodeURIComponent(
        `${assembly}.chr${variant.chrom}:${variant.pos}-${variant.pos}`
      )}`}
    />
  );
};

UCSCGeneView.propTypes = {
  variant: PropTypes.shape({
    annotations: PropTypes.arrayOf(
      PropTypes.shape({
        consequence: PropTypes.string,
        gene_id: PropTypes.string,
        gene_symbol: PropTypes.string,
        transcript_id: PropTypes.string,
      })
    ).isRequired,
    chrom: PropTypes.string.isRequired,
    pos: PropTypes.number.isRequired,
    reference_genome: PropTypes.oneOf(["GRCh37", "GRCh38"]).isRequired,
  }).isRequired,
};