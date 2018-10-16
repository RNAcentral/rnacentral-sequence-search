import React from 'react';

import Facets from 'pages/Result/components/Facets.jsx';
import Hit from 'pages/Result/components/Hit.jsx';

import 'pages/Result/index.scss';
import routes from 'services/routes.jsx';


class Result extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      status: "loading",
      results: [],
      facets: [],
      alignmentsCollapsed: true
    };

    this.onToggleAlignmentsCollapsed = this.onToggleAlignmentsCollapsed.bind(this);
  }

  onToggleAlignmentsCollapsed() {
    $('.alignment').toggleClass('alignment-collapsed');
    this.setState({ alignmentsCollapsed: !this.state.alignmentsCollapsed });
  }

  componentDidMount() {
    fetch(routes.jobResult(this.props.match.params.resultId))
      .then(response => response.json())
      .then(data => { this.setState({results: data, status: "success"}); console.log(data); });
  }

  render() {
    return (
      <div className="row" key="results">
        <h1 className="margin-top-large margin-bottom-large">Results: { this.state.status === "loading" ? <i className="icon icon-functional spin" data-icon="s"/> : <small>{ this.state.results.length } total</small> }</h1>
        <div className="small-12 medium-10 medium-push-2 columns">
          <section>
            { this.state.results.map((result, index) => (
            <ul key={`${result}_${index}`}><Hit result={result} alignmentsCollapsed={this.state.alignmentsCollapsed} onToggleAlignmentsCollapsed={ this.onToggleAlignmentsCollapsed } /></ul>
            )) }
          </section>
        </div>
        <Facets resultId={this.props.match.params.resultId}></Facets>
      </div>
    )
  }
}

export default Result;