import React from 'react';

import Facets from 'pages/Result/components/Facets.jsx';


class Result extends React.Component {
  render() {
    return (
      <div className="small-12 medium-2 medium-pull-10 columns">
        <section>
          <div>
            <ul className="simple vertical menu facets">
              <legend><h5>Facets</h5></legend>
              <li><span className="facet"><input id="checkbox12" type="checkbox" /><label htmlFor="checkbox12">Multi-filter 1</label></span></li>
              <li><span className="facet"><input id="checkbox13" type="checkbox" /><label htmlFor="checkbox13">Multi-filter 2</label></span></li>
              <li><span className="facet"><input id="checkbox14" type="checkbox" /><label htmlFor="checkbox14">Multi-filter 3</label></span></li>
              <li><span className="facet"><input id="checkbox15" type="checkbox" /><label htmlFor="checkbox15">Multi-filter 4</label></span></li>
            </ul>
          </div>
        </section>
      </div>
    )
  }
}

export default Result;