import React from "react";
import { authAxios } from "../utils";
import {
  orderSummaryURL,
  OrderItemDeleteURL,
  addToCartURL,
  minusQuantityURL,
} from "../Constants";
import {
  Container,
  Header,
  Message,
  Segment,
  Dimmer,
  Loader,
  Table,
  Label,
  Button,
  Image,
  Icon,
} from "semantic-ui-react";
import { Link } from "react-router-dom";
import { connect } from "react-redux";
import { fetchCart } from "../store/actions/cart";

class OrderSumary extends React.Component {
  state = {
    data: null,
    error: null,
    loading: false,
  };
  componentDidMount() {
    this.handleFetchOrder();
  }

  handleFetchOrder = () => {
    this.setState({ loading: true });
    authAxios
      .get(orderSummaryURL)
      .then((res) => {
        this.setState({ data: res.data, loading: false });
      })
      .catch((err) => {
        if (err.response !== undefined && err.response.status === 404) {
          this.setState({
            error: "you currently does not have an order",
            loading: false,
          });
        } else {
          this.setState({ error: err, loading: false });
        }
      });
  };

  renderVariations = (order_item) => {
    let text = "";
    order_item.item_variations.forEach((itemV) => {
      text += `${itemV.variation.name}:${itemV.value}, `;
    });
    return text;
  };

  handleRemoveItem = (itemID) => {
    authAxios
      .delete(OrderItemDeleteURL(itemID))
      .then((res) => {
        this.handleFetchOrder();
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  handleFormatData = (iv) => {
    // [{id: 1}, {id: 2}] to [1,2]
    return Object.keys(iv).map((key) => iv[key].id);
  };

  handlePlusQuantity = (slug, item_variations) => {
    this.setState({ loading: true });
    item_variations = this.handleFormatData(item_variations);
    authAxios
      .post(addToCartURL, { slug, item_variations })
      .then((res) => {
        this.handleFetchOrder();
        this.props.fetchCart();
        this.setState({ loading: false });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  };

  handleMinusQuantity = (slug, item_variations) => {
    // this.setState({ loading: true });
    item_variations = this.handleFormatData(item_variations);
    authAxios
      .post(minusQuantityURL, { slug, item_variations })
      .then((res) => {
        console.log(res.data);
        this.handleFetchOrder();
        this.props.fetchCart();
        // this.setState({ loading: false });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  };

  render() {
    const { data, error, loading } = this.state;
    console.log(data);
    return (
      <Container>
        <Header>OrderSumary</Header>
        {error && (
          <Message negative>
            {/* <Message.Header>Your payment was unsuccessful</Message.Header> */}
            <p>{JSON.stringify(error)}</p>
          </Message>
        )}
        {loading && (
          <Segment>
            <Dimmer>
              <Loader inverted>Loading</Loader>
            </Dimmer>
            <Image src="/images/wireframe/short-paragraph.png" />
          </Segment>
        )}
        {data && (
          <Table celled style={{ textAlign: "center" }}>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell>Item #</Table.HeaderCell>
                <Table.HeaderCell>Item name</Table.HeaderCell>
                <Table.HeaderCell>Item price</Table.HeaderCell>
                <Table.HeaderCell>Item quantity</Table.HeaderCell>
                <Table.HeaderCell>Total item price</Table.HeaderCell>
              </Table.Row>
            </Table.Header>

            <Table.Body>
              {data.order_items.map((order_item, i) => {
                return (
                  <Table.Row key={order_item.id}>
                    <Table.Cell>{i}</Table.Cell>
                    <Table.Cell>
                      {order_item.item.title} -{" "}
                      {this.renderVariations(order_item)}
                    </Table.Cell>
                    <Table.Cell>$ {order_item.item.price}</Table.Cell>
                    <Table.Cell>
                      <Icon
                        name="minus"
                        color="red"
                        style={{ float: "left", cursor: "pointer" }}
                        onClick={() =>
                          this.handleMinusQuantity(
                            order_item.item.slug,
                            order_item.item_variations
                          )
                        }
                      />{" "}
                      {order_item.quantity}{" "}
                      <Icon
                        name="plus"
                        color="red"
                        style={{ float: "right", cursor: "pointer" }}
                        onClick={() =>
                          this.handlePlusQuantity(
                            order_item.item.slug,
                            order_item.item_variations
                          )
                        }
                      />
                    </Table.Cell>
                    <Table.Cell>
                      {order_item.item.discount_price && (
                        <Label color="green" size="mini" horizontal>
                          ON DISCOUNT
                        </Label>
                      )}
                      ${order_item.final_price}
                      <Icon
                        name="trash"
                        color="red"
                        style={{ float: "right", cursor: "pointer" }}
                        onClick={() => this.handleRemoveItem(order_item.id)}
                      />
                    </Table.Cell>
                  </Table.Row>
                );
              })}
              <Table.Row>
                <Table.Cell />
                <Table.Cell />
                <Table.Cell />
                <Table.Cell colSpan="2" textAlign="center">
                  Total: {data.total}
                </Table.Cell>
              </Table.Row>
            </Table.Body>

            <Table.Footer>
              <Table.Row>
                <Table.HeaderCell colSpan="5" textAlign="right">
                  <Link to="/checkout">
                    <Button color="yellow">Checkout</Button>
                  </Link>
                </Table.HeaderCell>
              </Table.Row>
            </Table.Footer>
          </Table>
        )}
      </Container>
    );
  }
}

export default connect(null, { fetchCart })(OrderSumary);
