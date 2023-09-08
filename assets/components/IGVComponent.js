import React, { useRef, useEffect } from "react";
import PropTypes from "prop-types";

import { Segment, List } from "semantic-ui-react";
import igv from "igv/dist/igv.esm";

const parseGCSPath = (gcsPath) => {
  // eslint-disable-next-line no-unused-vars
  const [_, ...path] = gcsPath.replace("gs://", "").split("/");

  const [filename, ext] = path[path.length - 1].split(".");
  const [chrom, pos, ref, alt, gt, sampleId, suffix] = filename.split("_");

  return { chrom, pos, ref, alt, gt, sampleId, suffix, ext };
};

const createTracks = ({ reads, endpoint }) => {
  if (!reads) {
    return [];
  }

  return reads.map((read) => {
    const { sampleId, ext } = parseGCSPath(read);

    let indexURL = null;
    if (ext === "cram") {
      indexURL = `${read}.crai`;
    } else if (ext === "bam") {
      indexURL = `${read}.bai`;
    } else {
      // eslint-disable-next-line no-console
      console.error(`Unknown read file format: '${read}'. Expected bam or cram.`);
    }

    return {
      name: sampleId,
      sourceType: "file",
      url: `${endpoint}/?file=${encodeURIComponent(read)}`.replace("//", "/"),
      indexURL: `${endpoint}/?file=${encodeURIComponent(indexURL)}`.replace("//", "/"),
      format: ext,
    };
  });
};

const baseStyle = {
  fontFamily: "open sans,helveticaneue,helvetica neue,Helvetica,Arial,sans-serif",
  margin: "5px",
};

const IGVComponent = ({ chrom, pos, reads, referenceGenome, endpoint, style }) => {
  const container = useRef();

  const genome = referenceGenome === "GRCh37" ? "hg19" : "hg38";
  const locusId = `${chrom}:${pos - 10}-${pos + 10}`;
  const tracks = createTracks({ reads, endpoint });

  if (process.env.NODE_ENV === "development") {
    return (
      <Segment placeholder textAlign="center">
        <p>
          IGV tracks for locus <b>{locusId}</b> relative to <b>{genome}</b>
        </p>
        {tracks.map((track) => (
          <List key={track.name}>
            <List.Item key={`${track.name}-name`}>{track.name}</List.Item>
            <List.Item key={`${track.name}-url`}>
              <a href={track.url}>{track.url}</a>
            </List.Item>
            <List.Item key={`${track.name}-index-url`}>
              <a href={track.indexURL}>{track.indexURL}</a>
            </List.Item>
          </List>
        ))}
      </Segment>
    );
  }

  // Empty deps is equivalent to componentDidMount
  useEffect(() => {
    const igvOptions = { genome, locus: locusId, tracks };
    igv.createBrowser(container.current, igvOptions);
  }, []);

  return <div id="igv-viewer" ref={container} style={{ ...baseStyle, ...style }} />;
};

IGVComponent.propTypes = {
  chrom: PropTypes.string.isRequired,
  pos: PropTypes.number.isRequired,
  reads: PropTypes.arrayOf(PropTypes.string).isRequired,
  referenceGenome: PropTypes.oneOf(["GRCh37", "GRCh38"]).isRequired,
  endpoint: PropTypes.string.isRequired,
  style: PropTypes.object, // eslint-disable-line react/forbid-prop-types
};

IGVComponent.defaultProps = {
  style: {},
};

export default IGVComponent;
