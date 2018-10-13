import React from 'react';
import {Route, Link, Redirect, Switch} from 'react-router-dom';
import 'ebi-framework/js/script.js';
import 'foundation-sites/dist/js/foundation.js';
import 'ebi-framework/js/foundationExtendEBI.js';
import 'jquery/dist/jquery.js';

// import 'foundation-sites/dist/css/foundation.css';
import 'ebi-framework/css/ebi-global.css';
import 'ebi-framework/css/theme-light.css';
// <link rel="stylesheet" href="//www.ebi.ac.uk/web_guidelines/EBI-Icon-fonts/v1.2/fonts.css" type="text/css" media="all" />
import 'font-awesome/css/font-awesome.css';
import 'pixeden-stroke-7-icon/pe-icon-7-stroke/dist/pe-icon-7-stroke.min.css';
import 'animate.css/animate.min.css';
import 'flag-icon-css/css/flag-icon.css';
import 'styles/style.scss';

import PropsRoute from 'components/PropsRoute.jsx'
import Header from 'components/Header/index.jsx';
import InnerHeader from 'components/InnerHeader/index.jsx';
import Footer from 'components/Footer/index.jsx';

import Search from 'pages/Search/index.jsx';
import Job from 'pages/Job/index.jsx';
import Result from 'pages/Result/index.jsx';


class Layout extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
    };
  }

  render() {
    return [
        <div id="skip-to" key="skip-to">
          <ul>
            <li><a href="#content">Skip to main content</a></li>
            <li><a href="#local-nav">Skip to local navigation</a></li>
            <li><a href="#global-nav">Skip to EBI global navigation menu</a></li>
            <li><a href="#global-nav-expanded">Skip to expanded EBI global navigation menu (includes all sub-sections)</a>
            </li>
          </ul>
        </div>,

        <Header key="Header" />,

        <div id="content" key="content">
          <div data-sticky-container>
            <InnerHeader key="InnerHeader" />
          </div>

          <section id="main-content-area" className="row" role="main">

            <div className="columns margin-top-large margin-bottom-large">
              <section>
                <Switch>
                  <PropsRoute exact path="/search" component={Search} />
                  <PropsRoute path="/job/:jobId" component={Job} />
                  <PropsRoute path="/result/:resultId" component={Result} />
                  <Redirect to="/search" />
                </Switch>
              </section>
            </div>

          </section>
        </div>,

        <Footer key="Footer" />
    ]
  }

  componentDidMount() {
    $(document).foundation();
    $(document).foundationExtendEBI();
  }

}

export default Layout;
