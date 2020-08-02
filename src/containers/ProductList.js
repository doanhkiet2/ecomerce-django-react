import React from "react";
import {
  Container,
  Button,
  Icon,
  Image,
  Item,
  Label,
  Segment,
  Dimmer,
  Loader,
  Message,
} from "semantic-ui-react";
import axios from "axios";
import { productListURL, addToCartURL } from "../Constants";
import { authAxios } from "../utils";
import { fetchCart } from "../store/actions/cart";
import { connect } from "react-redux";
import ChooseVariations from "../components/ChooseVariations";

class ProductList extends React.Component {
  state = {
    loading: false,
    error: null,
    data: [],
    formVisible: [],
  };
  componentDidMount() {
    this.setState({ loading: true });
    axios
      .get(productListURL)
      .then((res) => {
        console.log(res.data);
        this.setState({ data: res.data, loading: false });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  }

  handleAddtoCart = (slug) => {
    this.setState({ loading: true });
    // const tokenN = localStorage.getItem("token");
    authAxios
      .post(addToCartURL, { slug })
      .then((res) => {
        console.log(res.data);
        // update the cart count
        this.props.fetchCart();

        this.setState({ loading: false });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  };
  handleOnClickAdd = (haveVariation, slug, data) => {
    console.log(data);
    if (haveVariation) this.handleToggleForm(slug);
    else this.handleAddtoCart(slug);
  };

  handleToggleForm = (slug) => {
    const { formVisible } = this.state;
    if (formVisible[slug]) {
      this.setState({
        formVisible: { ...formVisible, [slug]: null },
      });
    } else {
      this.setState({
        formVisible: { ...formVisible, [slug]: slug },
      });
    }
  };

  CallBack = (err) => {
    this.props.fetchCart();
    this.setState({ error: err });
  };

  handleChooseVariationsCallBack = (err) => {
    this.props.fetchCart();
    this.setState({ error: err });
  };

  render() {
    const { data, error, loading, formVisible } = this.state;
    console.log(formVisible);
    return (
      <Container>
        {error && (
          <Message
            error
            header="There was some errors with your submission"
            content={JSON.stringify(error)}
          />
        )}
        {loading && (
          <Segment>
            <Dimmer active inverted>
              <Loader inverted>Loading</Loader>
            </Dimmer>

            <Image src="/images/wireframe/short-paragraph.png" />
          </Segment>
        )}
        <Item.Group divided>
          {data.map((item) => {
            return (
              // <Segment></Segment>
              <Item key={item.id}>
                <Item.Image src={item.image} />
                <Item.Content>
                  <Item.Header
                    as="a"
                    onClick={() => {
                      this.props.history.push(`products/${item.id}`);
                    }}
                  >
                    {item.title}
                  </Item.Header>
                  <Item.Meta>
                    <span className="cinema">{item.category}</span>
                  </Item.Meta>
                  <Item.Description>{item.description}</Item.Description>
                  <Item.Extra>
                    {item.discount_price}
                    <Label
                      color={
                        item.label === "primary"
                          ? "blue"
                          : item.label === "secondary"
                          ? "green"
                          : "olive"
                      }
                    >
                      {item.label}
                    </Label>
                    <Button
                      primary
                      floated="right"
                      icon
                      labelPosition="right"
                      cursor="pointer"
                      onClick={(e, data) => {
                        this.handleOnClickAdd(
                          item.variations.length > 0,
                          item.slug,
                          data
                        );
                      }}
                      style={{ marginBotton: "20px!important" }}
                    >
                      <Icon name="cart plus" />
                      Add to cart
                    </Button>

                    {/*  */}

                    {formVisible[item.slug] && (
                      <ChooseVariations
                        data={item}
                        callback={this.handleChooseVariationsCallBack}
                      />
                    )}
                    {/*  */}
                  </Item.Extra>
                </Item.Content>
              </Item>
            );
          })}
        </Item.Group>
      </Container>
    );
  }
}
const mapDispatchToProps = (dispatch) => {
  // console.log(fetchCart);
  return {
    fetchCart: () => dispatch(fetchCart()),
  };
};

export default connect(null, mapDispatchToProps)(ProductList);
