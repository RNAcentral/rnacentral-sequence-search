import React from 'react';

import Facets from 'pages/Result/components/Facets.jsx';
import Hit from 'pages/Result/components/Hit.jsx';

import 'pages/Result/index.scss';
import routes from 'services/routes.jsx';


class Result extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      results: [],
      facets: []
    };
  }

  componentDidMount() {
    fetch(routes.jobResult(this.props.match.params.resultId))
      .then(response => response.json())
      .then(data => { this.setState({results: data}); console.log(data); });
  }

  render() {
    return (
      <div className="row" key="results">
        <h1 className="margin-top-large margin-bottom-large">Results: <small>{ this.state.results.length } total</small></h1>
        <div className="small-12 medium-10 medium-push-2 columns">
          <section>
            { this.state.results.map(result => (
            <ul key={result}><Hit result={result} /></ul>
            )) }
          </section>
          <ul className="pagination" role="navigation" aria-label="Pagination">
            <li className="pagination-previous disabled">Previous <span className="show-for-sr">page</span></li>
            <li className="current"><span className="show-for-sr">You're on page</span> 1</li>
            <li><a href="#" aria-label="Page 2">2</a></li>
            <li><a href="#" aria-label="Page 3">3</a></li>
            <li><a href="#" aria-label="Page 4">4</a></li>
            <li className="ellipsis" aria-hidden="true"></li>
            <li><a href="#" aria-label="Page 12">12</a></li>
            <li><a href="#" aria-label="Page 13">13</a></li>
            <li className="pagination-next"><a href="#" aria-label="Next page">Next <span
              className="show-for-sr">page</span></a></li>
          </ul>
        </div>
        <Facets resultId={this.props.match.params.resultId}></Facets>
      </div>
    )
  }
}

export default Result;