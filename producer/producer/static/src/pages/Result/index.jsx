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
      entries: [],
      facets: [],
      hitCount: 0,
      page_size: 20,
      page: 1,
      selectedFacets: {},  // e.g. { facetId1: [facetValue1, facetValue2], facetId2: [facetValue3] }
      alignmentsCollapsed: true
    };

    this.onToggleAlignmentsCollapsed = this.onToggleAlignmentsCollapsed.bind(this);
    this.toggleFacet = this.toggleFacet.bind(this)
  }

  /**
   * Returns a promise of sequences search results, passed to text search and accompanied with facets.
   * See example of server response: https://www.ebi.ac.uk/ebisearch/swagger.ebi
   *
   * @param resultId - id of this sequence search
   * @param query - lucene query string, constructed from selectedFacets
   * @param page - number of page, starting from 1
   * @param page_size - number of entries per page
   * @returns {Promise<any>}
   */
  fetchSearchResults(resultId, query, page, page_size) {
    return fetch(routes.facetsSearch(resultId, query, page, page_size))
      .then(response => response.json());
  }

  /**
   * Builds text query for sending to text search backend from this.state.selectedFacets
   * @returns {string | *}
   */
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

  /**
   * Should be invoked, when user checks/unchecks a text search facet
   * @param facetId
   * @param facetValue
   */
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

    // start loading from the first page again
    this.setState({ page : 1 });
    this.fetchSearchResults(this.props.match.params.resultId, this.buildQuery(), 1, this.state.page_size)
      .then(data => {
        this.setState({selectedFacets: selectedFacets, facets: data.facets, result: data.entries, status: "success"});
      })
      .catch(reason => this.setState({ status: "error" }));
  }

  /**
   * Collapses/displays alignments in search results
   */
  onToggleAlignmentsCollapsed() {
    $('.alignment').toggleClass('alignment-collapsed');
    this.setState({ alignmentsCollapsed: !this.state.alignmentsCollapsed });
  }

  /**
   * Checks that the page was scrolled down to the bottom.
   * Load more entries, if available then.
   */
  onScroll() {
    // Checks that the page has scrolled to the bottom
    if (window.innerHeight + document.documentElement.scrollTop === document.documentElement.offsetHeight) {
      if (this.state.status === "success" && this.state.entries < this.state.hitCount) {
        this.setState({page: this.state.page + 1, status: "loading"});
        this.fetchSearchResults(this.props.match.resultId, this.buildQuery(), this.state.page, this.state.page_size)
          .then(data => { this.setState({entries: [...this.state.entries, ...data.entries], status: "success"}) })
          .catch(reason => this.setState({ status: "error" }));
      }
    }
  }

  componentDidMount() {
    this.fetchSearchResults(this.props.match.params.resultId, this.buildQuery(), 1, this.state.page_size)
      .then(data => {
        console.log(data);

        let selectedFacets = {};
        data.facets.map((facet) => { selectedFacets[facet.id] = []; });

        this.setState({
          status: "success",
          entries: [...data.entries],
          facets: [...data.facets],
          hitCount: 0,
          selectedFacets: selectedFacets,
        })
      })
      .catch(reason => this.setState({ status: "error" }));

    // When user scrolls down to the bottom of the component, load more entries, if available.
    window.onscroll = this.onScroll;
  }

  render() {
    return (
      <div className="row">
        <h1 className="margin-top-large margin-bottom-large">Results: { this.state.status === "loading" ? <i className="icon icon-functional spin" data-icon="s"/> : <small>{ this.state.entries.length } total</small> }</h1>
        <div className="small-12 medium-10 medium-push-2 columns">
          <section>
            { this.state.entries.map((entry, index) => (
            <ul key={`${entry}_${index}`}><Hit entry={entry} alignmentsCollapsed={this.state.alignmentsCollapsed} onToggleAlignmentsCollapsed={ this.onToggleAlignmentsCollapsed } /></ul>
            )) }
          </section>
        </div>
        <Facets facets={ this.state.facets } selectedFacets={ this.state.selectedFacets } toggleFacet={ this.toggleFacet } />
      </div>
    )
  }
}

export default Result;