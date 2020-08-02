import React, { Component } from "react";
import {
  Grid,
  Header,
  Divider,
  Menu,
  Form,
  Segment,
  Dimmer,
  Message,
  Image,
  Loader,
  Select,
  Card,
  Label,
  Button,
  Table,
  Icon,
} from "semantic-ui-react";
import {
  addressListURL,
  addressCreateURL,
  countryListURL,
  userIDURL,
  addressUpdateURL,
  addressDeleteURL,
  paymentListURL,
} from "../Constants";

import { authAxios } from "../utils";
import { connect } from "react-redux";
import { Redirect } from "react-router-dom";
import _ from "lodash";

const UPDATEFORM = "UPDATE_FORM";
const CREATEFORM = "CREATE_FORM";

class PaymentHistory extends Component {
  state = {
    loading: false,
    err: null,
    payments: [],
    column: null,
    direction: null,
  };
  componentDidMount() {
    this.handleFetchPayments();
  }

  handleFetchPayments = () => {
    this.setState({ loading: true });
    authAxios
      .get(paymentListURL)
      .then((res) => {
        console.log(res.data);
        this.setState({
          loading: false,
          payments: res.data,
        });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  };

  // TOKNOW: why need _
  handleSort = (clickedColumn) => () => {
    const { column, payments, direction } = this.state;

    if (column !== clickedColumn) {
      this.setState({
        column: clickedColumn,
        payments: _.sortBy(payments, [clickedColumn]),
        direction: "ascending",
      });

      return;
    }

    this.setState({
      payments: payments.reverse(),
      direction: direction === "ascending" ? "descending" : "ascending",
    });
  };

  render() {
    const { column, payments, direction } = this.state;

    return (
      <Table sortable celled fixed>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>#</Table.HeaderCell>
            <Table.HeaderCell
              sorted={column === "id" ? direction : null}
              onClick={this.handleSort("id")}
            >
              ID
            </Table.HeaderCell>
            <Table.HeaderCell
              sorted={column === "amount" ? direction : null}
              onClick={this.handleSort("amount")}
            >
              Amount
            </Table.HeaderCell>
            <Table.HeaderCell
              sorted={column === "timestamp" ? direction : null}
              onClick={this.handleSort("timestamp")}
            >
              Date
            </Table.HeaderCell>
          </Table.Row>
        </Table.Header>

        <Table.Body>
          {payments &&
            _.map(payments, ({ id, amount, timestamp }, i) => {
              return (
                <Table.Row key={id}>
                  <Table.Cell>{i + 1}</Table.Cell>
                  <Table.Cell>
                    <Label ribbon>{id}</Label>
                  </Table.Cell>
                  <Table.Cell>${amount}</Table.Cell>
                  <Table.Cell>{new Date(timestamp).toUTCString()}</Table.Cell>
                </Table.Row>
              );
            })}
        </Table.Body>

        <Table.Footer>
          <Table.Row>
            <Table.HeaderCell colSpan="3">
              <Menu floated="right" pagination>
                <Menu.Item as="a" icon>
                  <Icon name="chevron left" />
                </Menu.Item>
                <Menu.Item as="a">1</Menu.Item>
                <Menu.Item as="a">2</Menu.Item>
                <Menu.Item as="a">3</Menu.Item>
                <Menu.Item as="a">4</Menu.Item>
                <Menu.Item as="a" icon>
                  <Icon name="chevron right" />
                </Menu.Item>
              </Menu>
            </Table.HeaderCell>
          </Table.Row>
        </Table.Footer>
      </Table>
    );
  }
}

class AddressForm extends Component {
  state = {
    error: null,
    loading: false,
    formData: {
      address_type: "",
      apartment_address: "",
      country: { code: "", name: "" },
      default: false,
      id: "",
      street_address: "",
      user: "",
      zip: "",
    },
    saving: false,
    success: false,
  };

  componentDidMount() {
    const { address, formtype } = this.props;

    if (formtype === UPDATEFORM) {
      this.setState({ formData: address }, () => {
        console.log(address);
      });
    }
  }

  handleToggleChange = (e, { name }) => {
    const { formData } = this.state;
    const updateFormData = {
      ...formData,
      [name]: !formData[name],
    };
    console.log(updateFormData);
    this.setState({
      formData: updateFormData,
    });
  };
  handleChange = (e, { name, value }) => {
    console.log(name);

    const { formData } = this.state;
    const updateFormData = {
      ...formData,
      [name]: value,
    };
    console.log(updateFormData);
    this.setState({
      formData: updateFormData,
    });
  };

  handleSubmit = (e, formtype) => {
    console.log(formtype);
    e.preventDefault();
    this.setState({ saving: true });
    if (formtype === "UPDATE_FORM") {
      this.handleUpdateAddress();
    } else {
      this.handleCreateAddress();
    }
  };

  handleCreateAddress = (e) => {
    const { activeItem, userID } = this.props;
    const { formData } = this.state;

    authAxios
      .post(addressCreateURL, {
        ...formData,
        user: userID,
        address_type: activeItem === "billingAddress" ? "B" : "S",
      })
      .then((res) => {
        console.log(res.data);
        this.props.callBack(); //fetchAddress, selectedAddress Null
        this.setState({
          saving: false,
          success: true,
          loading: false,
          formData: {
            address_type: "",
            apartment_address: "",
            country: { code: "", name: "" },
            default: false,
            id: "",
            street_address: "",
            user: "",
            zip: "",
          },
        });
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  handleUpdateAddress = (e) => {
    const { activeItem, userID } = this.props;
    const { formData } = this.state;

    authAxios
      .put(addressUpdateURL(formData.id), {
        ...formData,
        user: userID,
        address_type: activeItem === "billingAddress" ? "B" : "S",
      })
      .then((res) => {
        this.props.callBack();
        this.props.setState({ saving: false, success: true, loading: false });
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  handleStop = (e) => {
    e.preventDefault();
    this.props.handleSelectedAddress(null);
  };
  render() {
    const { countries, formtype } = this.props;
    const { error, saving, success, formData } = this.state;
    console.log(error);
    return (
      <React.Fragment>
        <Segment inverted={formtype === "UPDATE_FORM"}>
          <Form
            onSubmit={(e) => this.handleSubmit(e, formtype)}
            success={success}
            error={error !== null}
            inverted={formtype === "UPDATE_FORM"}
          >
            <Header color="blue">
              {formtype === "UPDATE_FORM" ? "Update" : "Add"}
            </Header>
            {success && (
              <Message
                success
                header="Success!"
                content="Your address was save"
              />
            )}
            <Form.Input
              required
              name="street_address"
              placeholder="Street address"
              onChange={this.handleChange}
              value={formData.street_address}
            />
            <Form.Input
              name="apartment_address"
              placeholder="Apartment address"
              onChange={this.handleChange}
              value={formData.apartment_address}
            />
            <Form.Field required>
              <Select
                loading={countries.length < 1}
                clearable
                search
                fluid
                options={countries}
                name="country"
                placeholder="country"
                onChange={this.handleChange}
                value={formData.country.code}
              />
            </Form.Field>

            <Form.Input
              required
              name="zip"
              placeholder="Zip code"
              onChange={this.handleChange}
              value={formData.zip}
            />
            {/* <Form.Input name="address_type" placeholder="Address type" /> */}
            <Form.Checkbox
              name="default"
              label="Make this the default address"
              onChange={this.handleToggleChange}
              checked={formData.default}
            />
            {success && (
              <Message
                success
                header="Success!"
                content="Your address was saved"
              />
            )}
            {error && (
              <Message
                error
                header="There was an error"
                content={JSON.stringify(error)}
              />
            )}
            {formtype === "UPDATE_FORM" && (
              <Form.Button
                primary
                floated="right"
                onClick={(e) => this.handleStop(e)}
              >
                Not Update
              </Form.Button>
            )}

            <Form.Button loading={saving} disabled={saving} primary>
              Save
            </Form.Button>
          </Form>
        </Segment>
      </React.Fragment>
    );
  }
}

class Profile extends React.Component {
  state = {
    activeItem: "billingAddress",
    addresses: [],
    userID: null,
    countries: [],
    error: null,
    loading: null,
    selectedAddress: null,
  };

  componentDidMount = () => {
    this.handlefetchAddress();
    this.handlefetchCountry();
    this.handlefetchUserID();
  };

  handlefetchUserID = () => {
    authAxios
      .get(userIDURL)
      .then((res) => {
        console.log(res.data);
        this.setState({ userID: res.data.userID });
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  //TOKNOW : what is async
  handleAddressItemClick = (e, { name }) => {
    this.setState({ activeItem: name }, () => {
      this.handlefetchAddress();
      this.handleSelectedAddress(null);
    });
  };

  handleGetActiveItem = () => {
    const { activeItem } = this.state;
    const result =
      activeItem === "billingAddress"
        ? "Billing Address"
        : activeItem === "shippingAddress"
        ? "Shipping Address"
        : "Payment History";
    return result;
  };

  handleFormatCountries = (countries) => {
    const keys = Object.keys(countries);
    return keys.map((k) => {
      return {
        key: k,
        text: countries[k],
        value: k,
      };
    });
  };
  handlefetchCountry = () => {
    authAxios
      .get(countryListURL)
      .then((res) => {
        this.setState({ countries: this.handleFormatCountries(res.data) });
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  handlefetchAddress = () => {
    this.setState({ loading: true });
    const { activeItem } = this.state;
    console.log(activeItem);
    authAxios
      .get(addressListURL(activeItem === "billingAddress" ? "B" : "S"))
      .then((res) => {
        this.setState({ addresses: res.data, loading: false });
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  handleDeleteAddress = (addressId) => {
    const { userID } = this.state;
    authAxios
      .delete(addressDeleteURL(addressId), {
        user: userID,
      })
      .then((res) => {
        console.log(res.data);
        this.handleCallBack();
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  handleSelectedAddress = (address) => {
    console.log(address);
    this.setState({ selectedAddress: address });
  };

  handleCallBack = () => {
    this.handlefetchAddress();
    this.setState({ selectedAddress: null });
  };

  renderAddresses = () => {
    const {
      activeItem,
      addresses,
      countries,
      selectedAddress,
      userID,
    } = this.state;
    return (
      <React.Fragment>
        <Card.Group>
          {addresses.map((a) => {
            return (
              <Card key={a.id}>
                <Card.Content>
                  <Label as="a" color="teal" ribbon="right">
                    <span style={{ color: "pink", fontSize: "1.2em" }}>
                      {a.default && "Default"}
                    </span>
                    &nbsp; &nbsp; &nbsp; &nbsp;{" "}
                    {activeItem === "billingAddress"
                      ? "Billing address"
                      : "Shipping address"}
                  </Label>

                  <Card.Header>address: {a.street_address}</Card.Header>
                  <Card.Header>apartment: {a.apartment_address}</Card.Header>
                  <Card.Meta>
                    {a.country.code}&nbsp; &nbsp; &nbsp; &nbsp;|&nbsp; &nbsp;
                    &nbsp; &nbsp;{a.country.name}
                  </Card.Meta>
                  <Card.Description>{a.zip}</Card.Description>
                </Card.Content>
                <Card.Content extra>
                  <div className="ui two buttons">
                    <Button
                      basic
                      color="yellow"
                      onClick={() => this.handleSelectedAddress(a)}
                    >
                      Update
                    </Button>
                    <Button
                      basic
                      color="red"
                      onClick={() => this.handleDeleteAddress(a.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </Card.Content>
              </Card>
            );
          })}
        </Card.Group>
        {addresses.length > 0 && <Divider />}
        {selectedAddress === null ? (
          <AddressForm
            userID={userID}
            activeItem={activeItem}
            countries={countries}
            addresses={addresses}
            formtype={CREATEFORM}
            callBack={this.handleCallBack}
            handleSelectedAddress={this.handleSelectedAddress}
          />
        ) : null}

        {selectedAddress && (
          <AddressForm
            activeItem={activeItem}
            userID={userID}
            countries={countries}
            address={selectedAddress}
            formtype={UPDATEFORM}
            callBack={this.handleCallBack}
            handleSelectedAddress={this.handleSelectedAddress}
          />
        )}
      </React.Fragment>
    );
  };

  render() {
    const { activeItem, error, loading } = this.state;
    const { isAuthenticated } = this.props;
    console.log(isAuthenticated);
    if (!isAuthenticated) {
      return <Redirect to="/login" />;
    }
    //need to know: why redirect to
    return (
      <Grid container columns={2} divided>
        <Grid.Row columns={1}>
          <Grid.Column>
            {error && (
              <Message
                error
                header="There was an errors "
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
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column width={4}>
            <Menu pointing vertical fluid>
              <Menu.Item
                name="billingAddress"
                active={activeItem === "billingAddress"}
                onClick={this.handleAddressItemClick}
              />
              <Menu.Item
                name="shippingAddress"
                active={activeItem === "shippingAddress"}
                onClick={this.handleAddressItemClick}
              />
              <Menu.Item
                name="paymentHistory"
                active={activeItem === "PaymentHistory"}
                onClick={this.handleAddressItemClick}
              />
            </Menu>
          </Grid.Column>
          <Grid.Column width={12}>
            <Header color="blue">
              Update your {this.handleGetActiveItem()}{" "}
            </Header>
            <Divider />
            {activeItem === "paymentHistory" ? (
              <PaymentHistory />
            ) : (
              this.renderAddresses()
            )}
          </Grid.Column>
        </Grid.Row>
      </Grid>
    );
  }
}

const mapStatetoProps = (state) => ({
  isAuthenticated: state.auth.token !== null,
});

export default connect(mapStatetoProps)(Profile);
