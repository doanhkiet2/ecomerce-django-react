import React, { Component } from "react";
import { Search } from "semantic-ui-react";
import { withRouter } from "react-router-dom";
import _ from "lodash";
import { searchURL, localhost } from "../Constants";
import axios from "axios";

const initialState = { isLoading: false, value: "", source: {} };
class SearchCategory extends Component {
  state = initialState;

  handleResultSelect = (e, { result }) =>
    this.setState({ value: result.title }, () => {
      console.log(result);
      const id = result.id;
      this.props.history.push(`/products/${id}`);
    });

  handleSearchChange = (e, { value }) => {
    this.setState({ isLoading: true, value }, () => {
      axios
        .get(searchURL, { params: { s_value: this.state.value } })
        .then((res) => {
          // convert array to dict, change image link, remove item with results = []
          //[{name:"D", results: Array(0), {name:"P", results: Array(1)}, {name:"S", results: Array(2)}}]
          //=> {P:{name:"P", results: Array(1)}, S:{name:"S", results: Array(2)}}
          let source = res.data.reduce((a, x) => {
            let newResults = x.results;
            newResults.forEach((searchItem) => {
              searchItem["image"] = `${localhost}${searchItem["image"]}`;
            });
            if (x.results.length > 0)
              return {
                ...a,
                [x.name]: { ...x, results: newResults },
              };
          }, {});
          console.log(source);

          this.setState({ source: source });
        })
        .catch((err) => {
          console.log(err);
        });
    });

    setTimeout(() => {
      if (this.state.value.length < 1) return this.setState(initialState);

      // const re = new RegExp(_.escapeRegExp(this.state.value), "i");
      // const isMatch = (result) =>
      //   re.test(result.title) || re.test(result.description);

      // const filteredResults = _.reduce(
      //   this.state.source,
      //   (memo, data, name) => {
      //     const results = _.filter(data.results, isMatch);
      //     if (results.length) memo[name] = { name, results }; // eslint-disable-line no-param-reassign
      //     console.log(memo);
      //     return memo;
      //   },
      //   {}
      // );

      this.setState({
        isLoading: false,
        //   results: filteredResults,
      });
    }, 200);
  };

  render() {
    console.log(this.context);
    const { isLoading, value, source } = this.state;

    return (
      <Search
        aligned="right"
        size="small"
        category
        loading={isLoading}
        onResultSelect={this.handleResultSelect}
        onSearchChange={_.debounce(this.handleSearchChange, 500, {
          leading: true,
        })}
        results={source}
        value={value}
      />
    );
  }
}
export default withRouter(SearchCategory);
