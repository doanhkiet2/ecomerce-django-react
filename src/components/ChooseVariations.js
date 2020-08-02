import React, { Component } from "react";
import {
  Image,
  Segment,
  Dimmer,
  Loader,
  Form,
  Divider,
  Select,
} from "semantic-ui-react";
import { addToCartURL } from "../Constants";
import { authAxios } from "../utils";

class ChooseVariations extends Component {
  state = { loading: false, formData: {} };

  handleFormatData = (formData) => {
    // console.log(Object.values(formData));
    return Object.keys(formData).map((key) => {
      return formData[key];
    });
  };

  handleAddtoCart = (slug) => {
    this.setState({ loading: true });
    // const tokenN = localStorage.getItem("token");
    const { formData } = this.state;
    const item_variations = this.handleFormatData(formData);
    authAxios
      .post(addToCartURL, { slug, item_variations })
      .then((res) => {
        console.log(res.data);
        // update the cart count
        // this.props.fetchCart();
        this.props.callback();

        this.setState({ loading: false });
      })
      .catch((err) => {
        this.setState({ loading: false });
        this.props.callback(err);
      });
  };

  handleChange = (e, { name, value }) => {
    const { formData } = this.state;
    const updatedFormData = {
      ...formData,
      [name]: value,
    };
    this.setState({ formData: updatedFormData });
  };
  render() {
    const { data } = this.props;
    const { loading, formData } = this.state;
    console.log(formData);
    return (
      <React.Fragment>
        <Divider />
        <Form>
          {loading && (
            <Segment>
              <Dimmer active inverted>
                <Loader inverted>Loading</Loader>
              </Dimmer>

              <Image src="/images/wireframe/short-paragraph.png" />
            </Segment>
          )}
          {data.variations &&
            data.variations.map((v) => {
              const name = v.name.toLowerCase();
              return (
                <Form.Field key={v.id}>
                  <Select
                    name={name}
                    onChange={this.handleChange}
                    options={v.item_variations.map((item) => {
                      return {
                        key: item.id,
                        text: item.value,
                        value: item.id,
                      };
                    })}
                    placeholder={`Choose a ${name}`}
                    selection
                    value={formData[name]}
                    // value={formData[name]}
                  />
                </Form.Field>
              );
            })}

          <Form.Button
            floated="right"
            fluid
            primary
            onClick={() => this.handleAddtoCart(data.slug)}
          >
            Add now
          </Form.Button>
        </Form>
      </React.Fragment>
    );
  }
}

export default ChooseVariations;
