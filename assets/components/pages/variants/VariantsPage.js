import React from "react";
import { Link } from "react-router-dom";
import { Header, Item } from "semantic-ui-react";

import DocumentTitle from "../../DocumentTitle";
import Fetch from "../../Fetch";
import VariantId from "../../VariantId";
import Page from "../Page";
import VariantSearch from "./VariantSearch";

const VariantsPage = () => (
  <Page>
    <DocumentTitle title="Variants" />
    <Header as="h1" dividing>
      Variants
    </Header>

    <VariantSearch />

    <Fetch path="/variants/">
      {({ data: { variants } }) => (
        // eslint-disable-next-line react/jsx-no-useless-fragment
        <React.Fragment>
          {variants.length > 0 ? (
            <Item.Group>
              {variants.map((variant) => (
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
            <p>No variants.</p>
          )}
        </React.Fragment>
      )}
    </Fetch>
  </Page>
);

export default VariantsPage;
