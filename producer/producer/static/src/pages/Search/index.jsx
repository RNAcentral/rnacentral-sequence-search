import React from 'react';

import routes from 'services/routes.jsx';

import 'pages/Search/index.scss';


class Search extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      rnacentralDatabases: [],
    };
  }

  render() {
    return (
      <div className="row">
        <div className="col-lg-12">
          <div className="hpanel">
            <div className="panel-heading">
              <h1>Search an RNA sequence in RNA databases</h1>
            </div>
            <div className="panel-body">
              <form>
                <div className="jd_toolParameterBox">
                  <fieldset>
                    <h4>RNA sequence:</h4>
                    <p>
                      <label>
                        Use a <a href="#" id="exampleSeq">example sequence</a> | <a href="#" id="clearSequence">Clear sequence</a> | <a href="#" id="seeMoreExample">See more example inputs</a>
                      </label>
                    </p>
                    <textarea id="sequence" name="sequence" rows="7"></textarea>
                    <p>
                      Or upload a file:
                      <input id="upfile" name="upfile" type="file"/>
                    </p>
                  </fieldset>
                </div>
                <div className="jd_toolParameterBox">
                  <fieldset>
                    <h4>RNA databases:</h4>
                    <ul id="rnacentralDatabases" className="facets">
                      {this.state.rnacentralDatabases.map(database =>
                        <li key={database}><span className="facet"><input id={database} type="checkbox" /><label htmlFor={database}>{database}</label></span></li>
                      )}
                    </ul>
                  </fieldset>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    )
  }

  componentDidMount() {
    fetch(routes.rnacentralDatabases)
      .then(response => response.json())
      .then(data => this.setState({ rnacentralDatabases: data }));
  }

}

export default Search;
