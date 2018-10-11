import React from 'react';
import {Route, Link, Redirect, Switch} from 'react-router-dom';
import 'ebi-framework/js/script.js';
import 'ebi-framework/js/foundationExtendEBI.js';
import 'foundation-sites/dist/js/foundation.js';
import 'jquery/dist/jquery.js';

import 'foundation-sites/dist/css/foundation.css';
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


// <!-- JavaScript -->
// <!-- Grab Google CDN's jQuery, with a protocol relative URL; fall back to local if offline -->
// <!--
// <script>window.jQuery || document.write('<script src="../js/libs/jquery-1.10.2.min.js"><\/script>')</script>
// -->
// <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
// <!-- Your custom JavaScript file scan go here... change names accordingly -->
// <!--
// <script defer="defer" src="//www.ebi.ac.uk/web_guidelines/js/plugins.js"></script>
// <script defer="defer" src="//www.ebi.ac.uk/web_guidelines/js/script.js"></script>
// -->
//
// <script defer="defer" src="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/js/script.js"></script>
//
// <!-- The Foundation theme JavaScript -->
// <script src="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/libraries/foundation-6/js/foundation.js"></script>
// <script src="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/js/foundationExtendEBI.js"></script>
// <script type="text/JavaScript">$(document).foundation();</script>
// <script type="text/JavaScript">$(document).foundationExtendEBI();</script>


// <!-- CSS: implied media=all -->
// <!-- CSS concatenated and minified via ant build script-->
// <link rel="stylesheet" href="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/libraries/foundation-6/css/foundation.css" type="text/css" media="all" />
// <link rel="stylesheet" href="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/css/ebi-global.css" type="text/css" media="all" />
// <link rel="stylesheet" href="//www.ebi.ac.uk/web_guidelines/EBI-Icon-fonts/v1.2/fonts.css" type="text/css" media="all" />
//
// <!-- Use this CSS file for any custom styling -->
// <!--
//   <link rel="stylesheet" href="css/custom.css" type="text/css" media="all" />
// -->
//
// <!-- If you have a custom header image or colour -->
// <!--
// <meta name="ebi:masthead-color" content="#000" />
// <meta name="ebi:masthead-image" content="//www.ebi.ac.uk/web_guidelines/EBI-Framework/images/backgrounds/embl-ebi-background.jpg" />
// -->
//
// <!-- you can replace this with theme-[projectname].css. See http://www.ebi.ac.uk/web/style/colour for details of how to do this -->
// <!-- also inform ES so we can host your colour palette file -->
// <link rel="stylesheet" href="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/css/theme-light.css" type="text/css" media="all" />
// <link rel="stylesheet" href="dist/gp-style.css" type="text/css" media="all" />
// <link rel="stylesheet" href="style.css" type="text/css" media="all" />
// <!-- end CSS-->


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

            <div className="columns margin-top-large">
              <section>
                <Switch>
                  <PropsRoute exact path="/search" component={Search} />
                  <PropsRoute path="/job/:id" component={Job} />
                  <PropsRoute path="/result/:id" component={Result} />
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
