import React from 'react';

import Facets from 'pages/Result/components/Facets.jsx';


class Result extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
        job_id: "",
        facets: [],
        results: []
    };

    this.renderFacet = this.renderFacet.bind(this);
  }

  renderFacet(facet) {
    return ([
      <legend><h5>{ facet.label }</h5></legend>,
      facet.facetValues.map(facetValue => (
        <li><span className="facet"><input id="checkbox12" type="checkbox" /><label htmlFor="checkbox12">{ facetValue }</label></span></li>
      ))
    ]);
  }

  render() {
    return (
      <div className="small-12 medium-2 medium-pull-10 columns">
        <section>
          <div>
            <ul className="vertical menu facets">
              {
                this.state.facets.map(facet => renderFacet(facet))
              }
            </ul>
          </div>
          <hr />
          <small className="text-muted">
            Powered by <a href="http://www.ebi.ac.uk/ebisearch/" target="_blank">EBI Search</a>
          </small>
        </section>
      </div>
    )
  }
}

export default Result;