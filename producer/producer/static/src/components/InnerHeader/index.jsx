import React from 'react';

class InnerHeader extends React.Component {
  render() {
    return (
      <header id="masthead" className="masthead" data-sticky data-sticky-on="large" data-top-anchor="content:top"
              data-btm-anchor="content:bottom">
        <div className="masthead-inner row">
          {/* local-title */}
          <div className="columns medium-12" id="local-title">
            <h1>
              <a href="#" title="Back to [service-name] homepage">RNA sequence search</a>
            </h1>
          </div>
          {/* /local-title */}
          {/* local-nav */}
          <nav>
            <ul id="local-nav" className="dropdown menu float-left" data-description="navigational">
              <li><a href="#home">Home</a></li>
              <li><a href="#hierarchy">Browse</a></li>
              <li><a href="#viewer">Viewer</a></li>
              <li><a href="#about">About</a></li>
            </ul>
          </nav>
          {/* /local-nav */}
        </div>
      </header>
    )
  }
}

export default InnerHeader;
