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
  Card,
  Grid,
  Header,
} from "semantic-ui-react";
import axios from "axios";
import { productDetaiURL } from "../Constants";
import { fetchCart } from "../store/actions/cart";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";
import ChooseVariations from "../components/ChooseVariations";

class ProductDetail extends React.Component {
  state = {
    loading: false,
    error: null,
    formVisible: false,
    formData: {},
    data: [],
  };
  componentDidMount() {
    this.handlefetchItem();
  }

  handleToggleForm = () => {
    const { formVisible } = this.state;
    this.setState({
      formVisible: !formVisible,
    });
  };

  handlefetchItem() {
    this.setState({ loading: true });
    //TOKNOW
    const {
      match: { params },
    } = this.props;
    axios
      .get(productDetaiURL(params.productID))
      .then((res) => {
        console.log(res.data);
        this.setState({ data: res.data, loading: false });
      })
      .catch((err) => {
        this.setState({ error: err, loading: false });
      });
  }

  handleChooseVariationsCallBack = (err) => {
    this.props.fetchCart();
    this.setState({ error: err });
  };
  render() {
    const { data, error, formVisible, loading } = this.state;
    const item = data;
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
        <Grid columns={2} divided>
          <Grid.Row>
            <Grid.Column>
              <Card
                fluid
                image={item.image}
                header={item.title}
                meta={
                  <React.Fragment>
                    {item.category}
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
                  </React.Fragment>
                }
                description={item.description}
                extra={
                  <React.Fragment>
                    <Button
                      fluid
                      color="yellow"
                      floated="right"
                      icon
                      labelPosition="right"
                      onClick={this.handleToggleForm}
                    >
                      <Icon name="cart plus" />
                      Add to cart
                    </Button>
                  </React.Fragment>
                }
              />
              {/*  */}
              {formVisible && (
                <ChooseVariations
                  data={data}
                  callback={this.handleChooseVariationsCallBack}
                />
              )}
              {/*  */}
            </Grid.Column>
            <Grid.Column>
              <Header as="h2">Try different variations</Header>
              <Grid columns={2} divided>
                <Grid.Row>
                  {item.variations &&
                    item.variations.map((v) => {
                      return (
                        <React.Fragment key={v.id}>
                          <Grid.Column>
                            <Header as="h3">{v.name}</Header>
                            <Item.Group divided>
                              {v.item_variations &&
                                v.item_variations.map((itemV) => {
                                  return (
                                    <Item key={itemV.id}>
                                      {itemV.attachment && (
                                        <Item.Image
                                          size="tiny"
                                          src={`http://127.0.0.1:8000${itemV.attachment}`}
                                        />
                                      )}
                                      <Item.Content
                                        content={itemV.value}
                                        verticalAlign="middle"
                                      />
                                    </Item>
                                  );
                                })}
                            </Item.Group>
                          </Grid.Column>
                        </React.Fragment>
                      );
                    })}
                </Grid.Row>
              </Grid>
            </Grid.Column>
          </Grid.Row>
        </Grid>
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

export default withRouter(connect(null, mapDispatchToProps)(ProductDetail));
