import React from 'react';

import routes from 'services/routes.jsx';


class Result extends React.Component {
  constructor(props) {
    super(props);

    this.renderFacet = this.renderFacet.bind(this);
  }

  renderFacet(facet) {
    return ([
      <legend key={facet.id}><h5 style={{color: 'rgb(0,124,130)' }}>{ facet.label }</h5></legend>,
      facet.facetValues.map(facetValue => (
        <li key={`li ${facetValue.label}`}>
          <span className="facet">
            <input id="checkbox12" type="checkbox" checked={ this.props.selectedFacets.hasOwnProperty(facet.id) && this.props.selectedFacets[facet.id].indexOf(facetValue.value) !== -1 } onChange={ (e) => this.props.toggleFacet(facet.id, facetValue.value) } />
            <label htmlFor="checkbox12">{ facetValue.label }</label>
          </span>
        </li>
      )),
      <br key={`br ${facet.id}`} />
    ]);
  }

  render() {
    return (
      <div className="small-12 medium-2 medium-pull-10 columns">
        <section>
          <div>
            <ul className="vertical menu facets">
              {
                this.props.facets.map(facet => this.renderFacet(facet))
              }
            </ul>
          </div>
          <small className="text-muted">
            Powered by <a href="http://www.ebi.ac.uk/ebisearch/" target="_blank">EBI Search</a>
          </small>
        </section>
      </div>
    )
  }
}

export default Result;