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
      selectedFacets: {},  // e.g. { facetId1: [facetValue1, facetValue2], facetId2: [facetValue3] }
      alignmentsCollapsed: true
    };

    this.onToggleAlignmentsCollapsed = this.onToggleAlignmentsCollapsed.bind(this);
    this.toggleFacet = this.toggleFacet.bind(this)
  }

  buildQuery() {
    let outputText, outputClauses = [];

    Object.keys(this.state.selectedFacets).map(facetId => {
      let facetText, facetClauses = [];
      this.state.selectedFacets[facetId].map(facetValue => facetClauses.push(`${facetId}: ${facetValue}`));
      facetText = facetClauses.join(" OR ");

      outputClauses.push("(" + facetText + ")");
    });

    outputText = outputClauses.join(" AND ");
    return outputText;
  }

  toggleFacet(facetId, facetValue) {
    let selectedFacets = { ...this.state.selectedFacets };

    if (Object.keys(this.state.selectedFacets).indexOf(facetId) === -1) {
      selectedFacets[facetId] = [facetValue];
    } else {
      let index = this.state.selectedFacets[facetId].indexOf(facetValue);
      if (index === -1) {
        selectedFacets[facetId].push(facetValue);
      } else {
        selectedFacets[facetId].splice(index, 1);
      }
    }

    fetch(routes.facetsSearch(this.props.match.params.resultId, this.buildQuery(), 1, 20))
      .then(response => response.json())
      .then(data => { this.setState({selectedFacets: selectedFacets, facets: data.facets, result: data.items, status: "success"}); });
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
        <Facets resultId={this.props.match.params.resultId} selectedFacets={ this.state.selectedFacets } toggleFacet={ this.toggleFacet } />
      </div>
    )
  }
}

export default Result;