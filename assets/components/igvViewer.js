import React, { createRef, Component } from "react";
import igv from "igv/dist/igv.esm";

const igvStyle = {
  fontFamily: "open sans,helveticaneue,helvetica neue,Helvetica,Arial,sans-serif",
  paddingTop: "60px",
  margin: "5px",
};

class IGViewerSection extends Component {
  constructor(props) {
    super(props);
    this.container = createRef();
  }

  componentDidMount() {
    if (this.container) {
      const igvOptions = {
        genome: "hg38",
        locus: "chr8:127,736,588-127,739,371",
        tracks: [
          {
            name: "HG00103",
            url:
              "https://s3.amazonaws.com/1000genomes/data/HG00103/alignment/HG00103.alt_bwamem_GRCh38DH.20150718.GBR.low_coverage.cram",
            indexURL:
              "https://s3.amazonaws.com/1000genomes/data/HG00103/alignment/HG00103.alt_bwamem_GRCh38DH.20150718.GBR.low_coverage.cram.crai",
            format: "cram",
          },
        ],
      };
      igv.createBrowser(this.container.current, igvOptions);
    }
  }

  render() {
    return <div id="igv-div" ref={this.container} style={igvStyle} />;
  }
}

export default IGViewerSection;
