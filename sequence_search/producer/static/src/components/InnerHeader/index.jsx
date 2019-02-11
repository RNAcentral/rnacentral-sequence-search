import React from 'react';
import {Link} from 'react-router-dom';

class InnerHeader extends React.Component {
  render() {
    return (
      <header id="masthead" className="masthead" data-sticky data-sticky-on="large" data-top-anchor="content:top"
              data-btm-anchor="content:bottom">
        <div className="masthead-inner row">
          {/* local-title */}
          <div className="columns medium-12" id="local-title">
            <h1>
              <Link to={`/search`}>RNA sequence search</Link>
            </h1>
          </div>
          {/* /local-title */}
          {/* local-nav */}
          <nav>
            <ul id="local-nav" className="dropdown menu float-left" data-description="navigational">
              <li><Link to={`/search`}>Search</Link></li>
              <li><Link to={`/documentation`}>Documentation</Link></li>
              <li><Link to={`/about`}>About</Link></li>
            </ul>
          </nav>
          {/* /local-nav */}
        </div>
      </header>
    )
  }
}

export default InnerHeader;
