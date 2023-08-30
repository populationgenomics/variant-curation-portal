import PropTypes from "prop-types";
import React, { useState } from "react";
import { Button, Form, Header, Message, Segment } from "semantic-ui-react";

const VARIANT_ID_REGEX = /^(\d+|X|Y)[-:]([0-9]+)[-:]([ACGT]+)[-:]([ACGT]+)$/;

const VariantIdForm = ({ onSubmit }) => {
  const [variantId, setVariantId] = useState("");

  const isValid = !!variantId.match(VARIANT_ID_REGEX);

  const showError = !!variantId && !isValid;

  return (
    <Form error={showError} onSubmit={() => onSubmit(variantId)}>
      <Form.Input
        error={showError}
        id="variant-search-variant-id"
        label="Variant ID"
        placeholder="chrom-pos-ref-alt"
        value={variantId}
        onChange={(e, { value }) => {
          setVariantId(value);
        }}
      />
      <Message error content="Invalid variant ID" />
      <Button disabled={!variantId || !isValid} type="submit">
        Search
      </Button>
      <Button
        type="reset"
        onClick={() => {
          setVariantId("");
          onSubmit(null);
        }}
      >
        Clear
      </Button>
    </Form>
  );
};

VariantIdForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
};

const fetchVariantIdFromClingenRegistry = (canonicalAlleleId, resolveLiftover = true) => {
  const promise = fetch(`https://reg.clinicalgenome.org/allele/${canonicalAlleleId.toUpperCase()}`)
    .then(null, () => {
      throw new Error("Error querying ClinGen Allele Registry");
    })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }

      if (response.status === 404) {
        throw new Error("Allele not found");
      } else {
        throw new Error("Error querying ClinGen Allele Registry");
      }
    })
    .then((response) => {
      const record = response.externalRecords.gnomAD || response.externalRecords.ExAC;
      if (!record) {
        throw new Error("No variant ID found for this allele");
      }

      return record[0].id;
    });

  if (resolveLiftover) {
    // ClinGen Alelle Registry only returns GRCh37 variant ids.
    return promise.then((variantId) => {
      const query = `
      {
        liftover(source_variant_id: "${variantId}", reference_genome: GRCh37) {
          liftover {
            variant_id
          }
        }
      }`;

      return fetch(`https://gnomad.broadinstitute.org/api?query=${query}`)
        .then(null, () => {
          throw new Error("Error querying gnomAD API");
        })
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          throw new Error("Error querying gnomAD API");
        })
        .then((response) => {
          const liftoverVariantId = response.data?.liftover[0]?.liftover?.variant_id;
          if (!variantId) {
            throw new Error(`No liftover variant ID found for '${canonicalAlleleId}/${variantId}'`);
          }

          // Callback expects anything with the 'includes' method
          return [variantId, liftoverVariantId].join("|");
        });
    });
  }

  return promise;
};

const ClingenAlleleIdForm = ({ onMatch, resolveLiftover }) => {
  const [caId, setCaId] = useState("");
  const [errorMessage, setErrorMessage] = useState(null);
  const [isFetching, setIsFetching] = useState(false);

  const isValid = !!caId.match(/^CA\d+$/i);

  const showError = (!!caId && !isValid) || !!errorMessage;

  return (
    <Form
      error={showError}
      onSubmit={() => {
        setIsFetching(true);
        setErrorMessage(null);
        fetchVariantIdFromClingenRegistry(caId, resolveLiftover).then(
          (variantId) => {
            setIsFetching(false);
            onMatch(variantId);
          },
          (err) => {
            setIsFetching(false);
            setErrorMessage(err.message);
          }
        );
      }}
    >
      <p>
        <b>Note:</b> ClinGen Allele Registry can only match against GRCh37 variant ids. Variants
        will be omitted from the search results if a liftover variant id cannot be found.
      </p>
      <Form.Input
        disabled={isFetching}
        error={showError}
        id="variant-search-clingen-allele-id"
        label="ClinGen Canonical Allele ID"
        placeholder="CA123123"
        value={caId}
        onChange={(e, { value }) => {
          setCaId(value);
        }}
      />
      {errorMessage && (
        <Message error content={errorMessage} onDismiss={() => setErrorMessage(null)} />
      )}
      {!isValid && <Message error content="Invalid canonical allele ID" />}
      <Button disabled={!caId || !isValid || isFetching} type="submit">
        Search
      </Button>
      <Button
        type="reset"
        onClick={() => {
          setCaId("");
          onMatch(null);
        }}
      >
        Clear
      </Button>
    </Form>
  );
};

ClingenAlleleIdForm.propTypes = {
  onMatch: PropTypes.func.isRequired,
  resolveLiftover: PropTypes.bool,
};

ClingenAlleleIdForm.defaultProps = {
  resolveLiftover: true,
};

const VariantSearch = ({ onSearch }) => {
  const [searchType, setSearchType] = useState("VariantID");
  return (
    <Segment attached>
      <Header as="h4">Look up variant</Header>

      <Form>
        <Form.Group inline>
          {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
          <label>Look up by</label>
          <Form.Radio
            id="variant-search-type-variant-id"
            label="Variant ID"
            value="VariantID"
            checked={searchType === "VariantID"}
            onChange={(e, { value }) => {
              setSearchType(value);
              onSearch(null);
            }}
          />
          <Form.Radio
            id="variant-search-type-caid"
            label="ClinGen Canonical Allele ID"
            value="CAID"
            checked={searchType === "CAID"}
            onChange={(e, { value }) => {
              setSearchType(value);
              onSearch(null);
            }}
          />
        </Form.Group>
      </Form>

      {searchType === "VariantID" && <VariantIdForm onSubmit={onSearch} />}
      {searchType === "CAID" && <ClingenAlleleIdForm onMatch={onSearch} resolveLiftover />}
    </Segment>
  );
};

VariantSearch.propTypes = {
  onSearch: PropTypes.func.isRequired,
};

export default VariantSearch;
