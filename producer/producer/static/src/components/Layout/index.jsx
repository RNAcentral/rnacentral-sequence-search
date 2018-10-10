import React from 'react';
import {Route, Link, Redirect, Switch} from 'react-router-dom';

import 'bootstrap/dist/css/bootstrap.css';
import 'font-awesome/css/font-awesome.css';
import 'pixeden-stroke-7-icon/pe-icon-7-stroke/dist/pe-icon-7-stroke.min.css';
import 'animate.css/animate.min.css';
import 'flag-icon-css/css/flag-icon.css';
import 'styles/style.scss';


import PropsRoute from 'components/PropsRoute.jsx'
import Header from 'components/Header/index.jsx';
import InnerHeader from 'components/InnerHeader/index.jsx';
import Footer from 'components/Footer/index.jsx';


// import Home from 'pages/Home.jsx';
// import Blog from 'pages/Blog.jsx';
// import Post from 'pages/Post.jsx';


class Layout extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
    };
  }

  render() {
    return [
      <body className="level2"><!-- add any of your classes or IDs -->
      <div id="skip-to">
        <ul>
          <li><a href="#content">Skip to main content</a></li>
          <li><a href="#local-nav">Skip to local navigation</a></li>
          <li><a href="#global-nav">Skip to EBI global navigation menu</a></li>
          <li><a href="#global-nav-expanded">Skip to expanded EBI global navigation menu (includes all sub-sections)</a>
          </li>
        </ul>
      </div>

      <Header key="Header" />,

      <div id="content">
        <div data-sticky-container>
          <InnerHeader key="InnerHeader" />
        </div>
        <!-- Suggested layout containers -->
        <section id="main-content-area" className="row" role="main">

          <div className="columns">
            <section>
              Placeholder
            </section>
          </div>

        </section>
        <!-- Optional local footer (insert citation / project-specific copyright / etc here -->
        <!--
        <footer id="local-footer" class="local-footer" role="local-footer">
          <div class="row">
            <span class="reference">How to reference this page: ...</span>
          </div>
        </footer>
        -->
        <!-- End optional local footer -->
      </div>
      <!-- End suggested layout containers / #content -->

      <Footer key="Footer" />

      <!-- JavaScript -->
      <!-- Grab Google CDN's jQuery, with a protocol relative URL; fall back to local if offline -->
      <!--
      <script>window.jQuery || document.write('<script src="../js/libs/jquery-1.10.2.min.js"><\/script>')</script>
      -->
      <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
      <!-- Your custom JavaScript file scan go here... change names accordingly -->
      <!--
      <script defer="defer" src="//www.ebi.ac.uk/web_guidelines/js/plugins.js"></script>
      <script defer="defer" src="//www.ebi.ac.uk/web_guidelines/js/script.js"></script>
      -->

      <script defer="defer" src="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/js/script.js"></script>

      <!-- The Foundation theme JavaScript -->
      <script src="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/libraries/foundation-6/js/foundation.js"></script>
      <script src="//www.ebi.ac.uk/web_guidelines/EBI-Framework/v1.2/js/foundationExtendEBI.js"></script>
      <script type="text/JavaScript">$(document).foundation();</script>
      <script type="text/JavaScript">$(document).foundationExtendEBI();</script>
      </body>
    ]
  }

  componentDidMount() {

  }

}

export default Layout;
