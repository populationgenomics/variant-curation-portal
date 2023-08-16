import React, { useRef, useEffect } from "react";
import PropTypes from "prop-types";
import { Segment, List } from "semantic-ui-react";
import igv from "igv/dist/igv.esm";

// name: PropTypes.string.isRequired,
// url: PropTypes.string.isRequired,
// indexURL: PropTypes.string.isRequired,
// format: PropTypes.oneOf(["bam", "cram"]).isRequired,
const DEFAULT_TRACKS = [
  {
    name: "HG00103",
    url: "https://s3.amazonaws.com/1000genomes/data/HG00103/alignment/HG00103.alt_bwamem_GRCh38DH.20150718.GBR.low_coverage.cram",
    indexURL:
      "https://s3.amazonaws.com/1000genomes/data/HG00103/alignment/HG00103.alt_bwamem_GRCh38DH.20150718.GBR.low_coverage.cram.crai",
    format: "cram",
  },
];

const baseStyle = {
  fontFamily: "open sans,helveticaneue,helvetica neue,Helvetica,Arial,sans-serif",
  margin: "5px",
};

const createTracks = ({ reads }) => {
  if (!reads) {
    return DEFAULT_TRACKS;
  }

  return reads.map((read) => {
    const sampleId = read.split("_")[4];

    let format = null;
    let indexURL = null;
    if (read.endsWith(".cram" || read.endsWith(".cram.gz"))) {
      format = "cram";
      indexURL = read.replace(".cram", ".cram.crai");
    } else if (read.endsWith(".bam" || read.endsWith(".bam.gz"))) {
      format = "bam";
      indexURL = read.replace(".bam", ".bam.bai");
    } else {
      console.error(`Unknown read file format: '${read}'. Expected bam or cram.`);
    }

    return { name: sampleId, url: read, indexURL, format };
  });
};

const IGVComponent = ({ variant, style }) => {
  const container = useRef();

  const { reference_genome: referenceGenome, chrom, pos, reads } = variant;
  const genome = referenceGenome === "GRCh37" ? "hg38" : "hg38";
  const locusId = `${chrom}:${pos + 10}-${pos + 10}`;
  const tracks = createTracks({ reads });

  if (process.env.NODE_ENV === "development") {
    return (
      <Segment placeholder textAlign="center">
        <p>IGV tracks:</p>
        {tracks.map((track) => (
          <>
            <List>
              <List.Item key={track.name}>{track.name}</List.Item>
              <List.Item key={`${track.name}-url`}>
                <a href={track.url}>{track.url}</a>
              </List.Item>
              <List.Item key={`${track.name}-index-url`}>
                <a href={track.indexURL}>{track.indexURL}</a>
              </List.Item>
            </List>
          </>
        ))}
      </Segment>
    );
  }

  // Empty deps is qquivalent to componentDidMount
  useEffect(() => {
    const igvOptions = { genome, locus: locusId, tracks };
    igv.createBrowser(container.current, igvOptions);
  }, []);

  return <div ref={container} style={{ ...baseStyle, ...style }} />;
};

IGVComponent.propTypes = {
  variant: PropTypes.shape({
    reference_genome: PropTypes.oneOf(["GRCh37", "GRCh38"]).isRequired,
    chrom: PropTypes.string.isRequired,
    pos: PropTypes.number.isRequired,
    reads: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  style: PropTypes.object, // eslint-disable-line react/forbid-prop-types
};

IGVComponent.defaultProps = {
  style: {},
};

export default IGVComponent;
