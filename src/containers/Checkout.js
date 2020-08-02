import React, { Component } from "react";
import { fetchCart } from "../store/actions/cart";

import {
  CardElement,
  injectStripe,
  Elements,
  StripeProvider,
} from "react-stripe-elements";
import {
  Container,
  Button,
  Message,
  Item,
  Divider,
  Header,
  Segment,
  Dimmer,
  Loader,
  Image,
  Label,
  Form,
  Select,
} from "semantic-ui-react";
import { authAxios } from "../utils";
import {
  cheackoutURL,
  orderSummaryURL,
  addCouponURL,
  addressListURL,
} from "../Constants";
import { Link, withRouter } from "react-router-dom";
import { connect } from "react-redux";

const OrderPreview = (props) => {
  const { data } = props;
  return (
    <React.Fragment>
      {data && (
        <React.Fragment>
          <Item.Group relaxed>
            {data.order_items.map((order_item, i) => {
              return (
                <Item key={i}>
                  <Item.Image
                    size="tiny"
                    src={`http://127.0.0.1:8000${order_item.item.image}`}
                  />

                  <Item.Content verticalAlign="middle">
                    <Item.Header as="a">
                      {order_item.item.title} x {order_item.item.title}
                    </Item.Header>
                    <Item.Extra>
                      <Label>{order_item.final_price}</Label>
                    </Item.Extra>
                  </Item.Content>
                </Item>
              );
            })}
          </Item.Group>
          <Item.Group>
            <Item>
              <Item.Content>
                <Item.Header>Order Total: ${data.total}</Item.Header>
                {data.coupon && (
                  <Label color="green" style={{ marginLeft: "10px" }}>
                    Current Coupon: {data.coupon.code}
                    &nbsp;&nbsp;for&nbsp;&nbsp;
                    {data.coupon.value}
                  </Label>
                )}
              </Item.Content>
            </Item>
          </Item.Group>
        </React.Fragment>
      )}
    </React.Fragment>
  );
};

class CouponForm extends Component {
  state = {
    code: "",
  };

  handleOnChangeCoupon = (e) => {
    this.setState({ [e.target.name]: e.target.value });
  };

  handleSubmit = (e) => {
    const { code } = this.state;
    this.props.handleAddCoupon(e, code);
    this.setState({ code: "" });
  };

  render() {
    const { code } = this.state;

    return (
      <React.Fragment>
        <Form onSubmit={this.handleSubmit}>
          <Form.Field>
            <label>Coupon Code</label>
            <input
              placeholder="Enter a coupon"
              onChange={this.handleOnChangeCoupon}
              name="code"
              value={code}
            />
          </Form.Field>
          <Button type="submit">Submit</Button>
        </Form>
      </React.Fragment>
    );
  }
}

class CheckoutForm extends Component {
  state = {
    loading: false,
    error: null,
    success: false,
    data: null,
    billingAddress: [],
    shippingAddress: [],
    selectedBillingAddress: "",
    selectedShippingAddress: "",
  };

  componentDidMount = () => {
    console.log("aaaaaaaaaaa", this.props.fetchCart);
    this.handlefetchOrder();
    this.handlefetchBillingAddress();
    this.handlefetchShippingAddress();
  };

  handleGetDefaultAddress = (addresses) => {
    const filteredAddress = addresses.filter((el) => el.default === true);
    console.log(filteredAddress);
    if (filteredAddress.length > 0) {
      console.log(filteredAddress[0].id);
      return filteredAddress[0].id;
    }
    return "";
  };

  handlefetchBillingAddress = () => {
    this.setState({ loading: true });
    authAxios
      .get(addressListURL("B"))
      .then((res) => {
        console.log(res.data);
        this.setState({
          billingAddress: res.data.map((a) => {
            return {
              key: a.id,
              text: `${a.street_address}, ${a.apartment_address},${a.country.code} | ${a.country.name}`,
              value: a.id,
            };
          }),
          selectedBillingAddress: this.handleGetDefaultAddress(res.data),
          loading: false,
        });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  };
  handlefetchShippingAddress = () => {
    this.setState({ loading: true });
    authAxios
      .get(addressListURL("S"))
      .then((res) => {
        console.log(res.data);
        this.setState({
          shippingAddress: res.data.map((a) => {
            return {
              key: a.id,
              text: `${a.street_address}, ${a.apartment_address},${a.country.code} | ${a.country.name}`,
              value: a.id,
            };
          }),
          selectedShippingAddress: this.handleGetDefaultAddress(res.data),
          loading: false,
        });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  };

  //Address
  handleSelectChange = (e, { name, value }) => {
    // console.log(e.target.name);
    // console.log(e.target.value);
    // console.log(name);
    // console.log(value);
    this.setState({ [name]: value });
  };

  handlefetchOrder = () => {
    this.setState({ loading: true });
    authAxios
      .get(orderSummaryURL)
      .then((res) => {
        this.setState({ data: res.data, loading: false });
      })
      .catch((err) => {
        if (err.response.status === 404) {
          console.log(err.response);
          this.setState({
            error: "you currently does not have an order",
            loading: false,
          });
          this.props.history.push("/products");
        } else {
          this.setState({ error: err, loading: false });
        }
      });
  };
  handleAddCoupon = (e, code) => {
    e.preventDefault();
    this.setState({ loading: true });
    authAxios
      .post(addCouponURL, { code })
      .then(() => {
        this.setState({ loading: false });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  };

  submit = (ev) => {
    ev.preventDefault();
    this.setState({ loading: true });
    if (this.props.stripe) {
      this.props.stripe.createToken().then((result) => {
        if (result.error) {
          this.setState({ error: result.error.message, loading: false });
        } else {
          this.setState({ error: null });
          const {
            selectedBillingAddress,
            selectedShippingAddress,
          } = this.state;
          authAxios
            .post(cheackoutURL, {
              stripeToken: result.token.id,
              selectedBillingAddress,
              selectedShippingAddress,
            })
            .then((res) => {
              console.log(res);
              this.setState({ loading: false, success: true });
              console.log(this.props.fetchCart);
              this.props.fetchCart();
            })
            .catch((err) => {
              console.log(err);
              console.log(err.message);
              this.setState({ loading: false, error: err });
            });
        }
      });
    } else {
      console.log("Stripe is not loaded");
    }
  };

  render() {
    const {
      error,
      loading,
      success,
      data,
      billingAddress,
      shippingAddress,
      selectedBillingAddress,
      selectedShippingAddress,
    } = this.state;

    return (
      <div>
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

        <OrderPreview data={data} />
        <Divider />
        <CouponForm
          handleAddCoupon={(e, code) => this.handleAddCoupon(e, code)}
        />
        <Divider />
        <Header>Select the billing address</Header>
        {billingAddress.length > 0 ? (
          <Select
            name="selectedBillingAddress"
            value={selectedBillingAddress}
            options={billingAddress}
            selection
            clearable
            onChange={this.handleSelectChange}
          />
        ) : (
          <p>
            You need to <Link to="/profile"> add addresses</Link>
          </p>
        )}
        <Header>Select the shipping address</Header>
        {shippingAddress.length > 0 ? (
          <Select
            name="selectedShippingAddress"
            value={selectedShippingAddress}
            options={shippingAddress}
            selection
            clearable
            onChange={this.handleSelectChange}
          />
        ) : (
          <p>
            You need to <Link to="/profile"> add a billing addresses</Link>
          </p>
        )}
        <Divider />

        {billingAddress.length < 1 || shippingAddress.length < 1 ? (
          <p>
            You need to add a shipping addresses before complete your purcharse
          </p>
        ) : (
          <React.Fragment>
            <Header>Would you like to complete the purcharse?</Header>
            <CardElement />
            {success && (
              <Message positive>
                <Message.Header>Your payment was successful</Message.Header>
                <p>
                  Go to your <b>profile</b> to see the order delivery status.
                </p>
              </Message>
            )}
            <Button
              primary
              style={{ marginTop: "15px", width: "20%" }}
              onClick={this.submit}
              loading={loading}
              disabled={loading}
            >
              Send
            </Button>
          </React.Fragment>
        )}
      </div>
    );
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchCart: () => dispatch(fetchCart()),
  };
};
const CheckoutFormConnect = connect(null, mapDispatchToProps)(CheckoutForm);

const InjectedForm = withRouter(injectStripe(CheckoutFormConnect));
const WrappedForm = () => (
  <Container text>
    <StripeProvider apiKey="pk_test_51H6g4WEIs0qYXInvc6Xk0JrPiXdcMRHXLl9TEiKh2HmYJsN5PvSW0Mx0C9Dx6Mvtc4gYuvLemyBOBBxE9tKTMW1U006QXCJAIS">
      <div>
        <h1>Complete your order</h1>
        <Elements>
          <InjectedForm />
        </Elements>
      </div>
    </StripeProvider>
  </Container>
);

export default WrappedForm;

/*
1. adding the order items in the payment view as a summary
2. adding discount code form in checkout view
*/
