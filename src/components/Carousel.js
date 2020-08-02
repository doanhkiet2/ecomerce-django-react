import React, { Component } from "react";
import { Modal, Image } from "semantic-ui-react";
import { localhost } from "../Constants";

class Viewer extends React.PureComponent {
  state = {
    index: this.props.index,
  };

  componentDidMount() {
    document.addEventListener("keydown", this.handleKey, false);
  }

  componentWillUnmount() {
    document.removeEventListener("keydown", this.handleKey, false);
  }

  handleKey = ({ key }) => {
    if (key === "ArrowRight") {
      this.flip(1);
    }
    if (key === "ArrowLeft") {
      this.flip(-1);
    }
  };

  flip(val) {
    this.setState(({ index }) => {
      let target = index + val;
      const { items } = this.props;
      if (target >= items.length) {
        target = 0;
      }
      if (target < 0) {
        target = items.length - 1;
      }
      return { index: target };
    });
  }

  render() {
    const { items } = this.props;
    const { index } = this.state;
    const { image } = items[index];
    const url = `${localhost}${image}`;
    return (
      <Modal.Content image>
        <Image wrapped src={url} />
      </Modal.Content>
    );
  }
}

const Photo = ({ path, items, index }) => {
  const url = `${localhost}${path}`;
  return (
    <Modal
      centered={true}
      trigger={<Image Fluid Centered size="large" src={url} alt="general" />}
      basic
      content={<Viewer items={items} index={index} />}
      actions={[{ key: "done", content: "OK", positive: true }]}
    />
  );
};

const Carousel = ({ items }) => (
  <Image.Group size="small">
    {items &&
      items.map &&
      items.map(({ image }, index) => (
        <Photo key={index} path={image} items={items} index={index} />
      ))}
  </Image.Group>
);

export default Carousel;
