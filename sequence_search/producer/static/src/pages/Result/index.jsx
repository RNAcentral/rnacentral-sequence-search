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
      selectedFacets: {},  // e.g. { facetId1: [facetValue1.value, facetValue2.value], facetId2: [facetValue3.value] }
      alignmentsCollapsed: true,
      textSearchError: false
    };

    this.onToggleAlignmentsCollapsed = this.onToggleAlignmentsCollapsed.bind(this);
    this.onScroll = this.onScroll.bind(this);
    this.toggleFacet = this.toggleFacet.bind(this);
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
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error(response.statusText);
        }
      });
  }

  /**
   * Builds text query for sending to text search backend from this.state.selectedFacets
   * @returns {string | *}
   */
  buildQuery() {
    let outputText, outputClauses = [];

    Object.keys(this.state.selectedFacets).map(facetId => {
      let facetText, facetClauses = [];
      this.state.selectedFacets[facetId].map(facetValueValue => facetClauses.push(`${facetId}: ${facetValueValue}`));
      facetText = facetClauses.join(" OR ");

      if (facetText !== "") outputClauses.push("(" + facetText + ")");
    });

    outputText = outputClauses.join(" AND ");
    return outputText;
  }

  /**
   * Should be invoked, when user checks/unchecks a text search facet
   * @param facetId
   * @param facetValueValue - facetValue.value
   */
  toggleFacet(facetId, facetValueValue) {
    let selectedFacets = { ...this.state.selectedFacets };

    if (!this.state.selectedFacets.hasOwnProperty(facetId)) {  // all values in clicked facet are unchecked
      selectedFacets[facetId] = [facetValueValue];
    } else {
      let index = this.state.selectedFacets[facetId].indexOf(facetValueValue);
      if (index === -1) { selectedFacets[facetId].push(facetValueValue); }  // this value is not checked, check it
      else { selectedFacets[facetId].splice(index, 1); }  // this value is checked, uncheck it
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
   *
   * Mostly stolen from: https://alligator.io/react/react-infinite-scroll/
   */
  onScroll() {
    // Checks that the page has scrolled to the bottom
    if (window.innerHeight + document.documentElement.scrollTop + 10 >= document.documentElement.offsetHeight) {
      if (this.state.status === "success" && this.state.entries.length < this.state.hitCount) {
        this.setState(
          (state, props) => (state.page === this.state.page ? { page: this.state.page + 1, status: "loading" } : { status: "loading" }),
          () => {
            this.fetchSearchResults(this.props.match.params.resultId, this.buildQuery(), this.state.page, this.state.page_size)
              .then(data => { this.setState({
                status: "success",
                entries: [...this.state.entries, ...data.entries],
                textSearchError: data.textSearchError
              }) })
              .catch(reason => this.setState({ status: "error" }));
          }
        );
      }
    }
  }

  componentDidMount() {
    this.fetchSearchResults(this.props.match.params.resultId, this.buildQuery(), 1, this.state.page_size)
      .then(data => {
        let selectedFacets = {};
        data.facets.map((facet) => { selectedFacets[facet.id] = []; });

        this.setState({
          status: "success",
          entries: [...data.entries],
          facets: [...data.facets],
          hitCount: data.hitCount,
          selectedFacets: selectedFacets,
          textSearchError: textSearchError
        });
      })
      .catch(reason => this.setState({ status: "error" }));

    // When user scrolls down to the bottom of the component, load more entries, if available.
    window.onscroll = this.onScroll;
  }

  render() {
    return (
      <div className="row">
        <h1 className="margin-top-large margin-bottom-large">Results: { this.state.status === "loading" ? <i className="icon icon-functional spin" data-icon="s"/> : <small>{ this.state.hitCount } total</small> }</h1>
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
