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
  List,
  Feed,
} from "semantic-ui-react";
import {
  addressListURL,
  addressCreateURL,
  countryListURL,
  userIDURL,
  addressUpdateURL,
  addressDeleteURL,
  paymentListURL,
  designerDetaiURL,
  localhost,
} from "../Constants";
import Carousel from "../components/Carousel";

import { authAxios } from "../utils";
import { connect } from "react-redux";
import { Redirect, withRouter } from "react-router-dom";
import _ from "lodash";
import axios from "axios";

const UPDATEFORM = "UPDATE_FORM";
const CREATEFORM = "CREATE_FORM";

class Profile extends React.Component {
  state = {
    activeItem: "profile",
    addresses: [],
    userID: null,
    countries: [],
    error: null,
    loading: null,
    selectedAddress: null,
    data: {},
  };

  componentDidMount = () => {
    this.handleFetchData();
  };

  handleFetchData = () => {
    const {
      match: { params },
    } = this.props;
    axios
      .get(designerDetaiURL(params.designerID))
      .then((res) => {
        console.log(res.data);
        this.setState({ data: res.data });
        //continuethis
      })
      .catch((err) => {
        this.setState({ error: err });
      });
  };

  //TOKNOW : what is async
  handleDivisionClick = (e, { name, pushid }) => {
    console.log(pushid);
    this.setState({ activeItem: name }, () => {});
    if (pushid) {
      this.props.history.push(`/designer/${pushid}`);
    }
  };

  handleGetActiveItem = () => {
    const { activeItem } = this.state;
    const result =
      activeItem === "profile"
        ? "Profile"
        : activeItem === "about"
        ? "About"
        : "Brand";
    return result;
  };

  handleSelectedDevision = (devision) => {
    this.setState({ selectedDevision: devision });
  };

  renderAddresses = () => {
    const {
      activeItem,
      addresses,
      countries,
      selectedAddress,
      userID,
      data,
    } = this.state;
    console.log(`${localhost} ${data.image}`);
    return (
      <React.Fragment>
        {selectedAddress === null ? (
          <Grid divided="vertically">
            <Grid.Row columns={3}>
              <Grid.Column>
                <Image src={data.image} />
              </Grid.Column>
              <Grid.Column>
                <List>
                  <List.Header as="h3">{data.name}</List.Header>
                  <List.Item>Style: {data.fashion_style}</List.Item>
                  <List.Item>
                    Brand: {data.brand ? data.brand.name : data.name}
                  </List.Item>
                </List>
              </Grid.Column>
              <Grid.Column>
                <List>
                  <List.Item icon="users" content="Semantic UI" />
                  <List.Item icon="marker" content="New York, NY" />
                  <List.Item
                    icon="mail"
                    content={<a href="">jack@semantic-ui.com</a>}
                  />
                  <List.Item
                    icon="linkify"
                    content={<a href="">semantic-ui.com</a>}
                  />
                </List>
              </Grid.Column>
              <Grid.Column>
                <Feed>
                  <Feed.Extra>
                    <Carousel items={data.items} />
                  </Feed.Extra>
                </Feed>
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>{data.description}</Grid.Row>
          </Grid>
        ) : null}
      </React.Fragment>
    );
  };

  render() {
    const { activeItem, error, loading } = this.state;
    console.log(activeItem);
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
                name="profile"
                active={activeItem === "profile"}
                onClick={this.handleDivisionClick}
              />
              <Menu.Item
                name="about"
                active={activeItem === "about"}
                onClick={this.handleDivisionClick}
              />
              <Menu.Item
                name="brand"
                pushid="1"
                active={activeItem === "brand"}
                onClick={this.handleDivisionClick}
              />
            </Menu>
          </Grid.Column>
          <Grid.Column width={12}>
            <Header color="blue">{this.handleGetActiveItem()} </Header>
            <Divider />
            {activeItem === "brand"
              ? "ffffffffff"
              : //   <brand />
                this.renderAddresses()}
          </Grid.Column>
        </Grid.Row>
      </Grid>
    );
  }
}

const mapStatetoProps = (state) => ({
  isAuthenticated: state.auth.token !== null,
});

export default withRouter(connect(mapStatetoProps)(Profile));
