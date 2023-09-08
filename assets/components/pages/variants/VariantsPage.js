import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Header, Item, Segment } from "semantic-ui-react";

import DocumentTitle from "../../DocumentTitle";
import Fetch from "../../Fetch";
import VariantId from "../../VariantId";
import Page from "../Page";
import VariantSearch from "./VariantSearch";

const VariantsPage = () => {
  const [searchTerms, setSearchTerms] = useState(null);

  return (
    <Page>
      <DocumentTitle title="Variants" />
      <Header as="h1" dividing>
        Variants
      </Header>

      <VariantSearch onSearch={setSearchTerms} />

      <Fetch path="/variants/">
        {({ data: { variants } }) => {
          const grch37 = variants
            .filter((variant) => variant.reference_genome === "GRCh37")
            .filter((variant) => {
              if (!searchTerms || !searchTerms.length) return true;
              return (
                searchTerms.includes(variant.variant_id) ||
                searchTerms.includes(variant.liftover_variant_id)
              );
            });

          const grch38 = variants
            .filter((variant) => variant.reference_genome === "GRCh38")
            .filter((variant) => {
              if (!searchTerms || !searchTerms.length) return true;
              return (
                searchTerms.includes(variant.variant_id) ||
                searchTerms.includes(variant.liftover_variant_id)
              );
            });

          // ClinGen search only returns GRCh37 variant ids. Match against both variant id and the
          // liftover id and then defer the choice to the user.
          const segments = [
            { segVariants: grch37, reference: "GRCh37" },
            { segVariants: grch38, reference: "GRCh38" },
          ];

          return (
            // eslint-disable-next-line react/jsx-no-useless-fragment
            <React.Fragment>
              {segments.map(({ segVariants, reference }) => (
                <Segment key={reference.toLowerCase()} attached="top">
                  <Header as="h4">{reference}</Header>
                  {segVariants.length > 0 ? (
                    <Item.Group>
                      {segVariants.map((variant) => (
                        <Item key={variant.variant_id}>
                          <Item.Content>
                            <Item.Header>
                              <Link to={`/variant/${variant.variant_id}/`}>
                                <VariantId variantId={variant.variant_id} />
                              </Link>
                            </Item.Header>
                          </Item.Content>
                        </Item>
                      ))}
                    </Item.Group>
                  ) : (
                    <p>No {reference} variants.</p>
                  )}
                </Segment>
              ))}
            </React.Fragment>
          );
        }}
      </Fetch>
    </Page>
  );
};

export default VariantsPage;
