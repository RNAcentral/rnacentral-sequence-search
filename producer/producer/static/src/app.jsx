import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter as Router, Route, Link, browserHistory} from 'react-router-dom';
import 'jquery/dist/jquery.js';


// load favicons with file loader, snippet of code is stolen from:
// https://medium.com/tech-angels-publications/bundle-your-favicons-with-webpack-b69d834b2f53
const faviconsContext = require.context(
  '!!file-loader?name=favicons/[name].[ext]!.',
  true,
  /\.(svg|png|ico|xml|json)$/
);
faviconsContext.keys().forEach(faviconsContext);

import Layout from 'pages/Layout.jsx'

import configureStore from 'store'

ReactDOM.render(
  <Router history={browserHistory}>
    <Route path="/" component={Layout} >
    </Route>
  </Router>,
  document.getElementById('main')
);
