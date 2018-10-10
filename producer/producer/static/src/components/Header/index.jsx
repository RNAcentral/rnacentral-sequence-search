import React from 'react';

class Header extends React.Component {
  render() {
    return (
      <header id="masthead-black-bar" className="clearfix masthead-black-bar">
        <nav className="row">
          <ul id="global-nav" className="menu">
            {/* set active class as appropriate */}
            <li className="home-mobile"><a href="//www.ebi.ac.uk"></a></li>
            <li className="home active"><a href="//www.ebi.ac.uk">EMBL-EBI</a></li>
            <li className="services"><a href="//www.ebi.ac.uk/services">Services</a></li>
            <li className="research"><a href="//www.ebi.ac.uk/research">Research</a></li>
            <li className="training"><a href="//www.ebi.ac.uk/training">Training</a></li>
            <li className="about"><a href="//www.ebi.ac.uk/about">About us</a></li>
            <li className="search">
              <a href="#" data-toggle="search-global-dropdown"><span className="show-for-small-only">Search</span></a>
              <div id="search-global-dropdown" className="dropdown-pane" data-dropdown
                   data-options="closeOnClick:true;">
                {/* The dropdown menu will be programatically added by script.js */}
              </div>
            </li>
            <li className="float-right show-for-medium embl-selector">
              <button className="button float-right" type="button" data-toggle="embl-dropdown">Hinxton</button>
              {/* The dropdown menu will be programatically added by script.js */}
            </li>
          </ul>
        </nav>
      </header>
    )
  }
}

export default Header;