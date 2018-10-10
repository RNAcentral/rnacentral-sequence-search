import React from 'react';

class InnerHeader extends React.Component {
  render() {
    return (
      <header id="masthead" className="masthead" data-sticky data-sticky-on="large" data-top-anchor="content:top"
              data-btm-anchor="content:bottom">
        <div className="masthead-inner row">
          <!-- local-title -->
          <div className="columns medium-12" id="local-title">
            <h1>
              <img
                src="https://raw.githubusercontent.com/ebi-pf-team/genome-properties/master/docs/_static/images/GP_logo.png"/>
              <a href="#" title="Back to [service-name] homepage">Genome Properties</a>
            </h1>
          </div>
          <!-- /local-title -->
          <!-- local-nav -->
          <nav>
            <ul id="local-nav" className="dropdown menu float-left" data-description="navigational">
              <li><a href="#home">Home</a></li>
              <li><a href="#hierarchy">Browse</a></li>
              <li><a href="#viewer">Viewer</a></li>
              <li><a href="#about">About</a></li>
            </ul>
          </nav>
          <!-- /local-nav -->
        </div>
      </header>
    )
  }
}

export default InnerHeader;

