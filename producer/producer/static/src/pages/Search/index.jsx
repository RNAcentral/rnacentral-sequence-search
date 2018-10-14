import React from 'react';
import { withRouter } from 'react-router-dom';

import routes from 'services/routes.jsx';

import 'pages/Search/index.scss';


class Search extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      rnacentralDatabases: [],
      selectedDatabases: {},
      sequence: "",
      submissionError: ""
    };
  }

  onSubmit(event) {
    event.preventDefault();

    fetch(routes.submitJob(), {
      method: 'post',
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({query: this.state.sequence, databases: Object.keys(this.state.selectedDatabases).filter(key => this.state.selectedDatabases[key]) })
    })
      .then(function(response) {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error(response.statusText);
        }
      })
      .then(data => {
        console.log(data);
        this.props.history.push(`/job/${data.job_id}`);
      })
      .catch(error => {
        console.log(error);
        this.setState({submissionError: error.toString()})
      });
  }

  onSequenceTextareaChange(event) {
    this.setState({sequence: event.target.value.toUpperCase()});
  }

  onDatabaseCheckboxToggle(event) {
    let selectedDatabases = { ...this.state.selectedDatabases };
    selectedDatabases[event.target.id] = !selectedDatabases[event.target.id];
    this.setState({ selectedDatabases: selectedDatabases });
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
              <form onSubmit={(e) => this.onSubmit(e)}>
                <div>
                  <fieldset>
                    <h4>RNA sequence:</h4>
                    <p>
                      <label>
                        Use a <a href="#" id="exampleSeq">example sequence</a> | <a href="#" id="clearSequence">Clear sequence</a> | <a href="#" id="seeMoreExample">See more example inputs</a>
                      </label>
                    </p>
                    <textarea id="sequence" name="sequence" rows="7" value={this.state.sequence} onChange={(e) => this.onSequenceTextareaChange(e)} />
                    <p>
                      Or upload a file:
                      <input id="upfile" name="upfile" type="file"/>
                    </p>
                  </fieldset>
                </div>
                { this.state.submissionError && <div className="callout alert">
                  <h3>Form submission failed</h3>
                  { this.state.submissionError }
                </div>}
                <div>
                  <fieldset>
                    <h4>RNA databases:</h4>
                    <ul id="rnacentralDatabases" className="facets">
                      {this.state.rnacentralDatabases.map(database =>
                        <li key={database}><span className="facet"><input id={database} type="checkbox" checked={this.state.selectedDatabases[database]} onChange={(e) => this.onDatabaseCheckboxToggle(e)} /><label htmlFor={database}>{database}</label></span></li>
                      )}
                    </ul>
                  </fieldset>
                </div>
                <div>
                  <fieldset>
                    <div id="jd_submitButtonPanel">
                      <input name="submit" type="submit" value="Submit" className="button" />
                    </div>
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
    fetch(routes.rnacentralDatabases())
      .then(response => response.json())
      .then(data => {
        let selectedDatabases = {};
        data.map(database => {selectedDatabases[database] = true});
        this.setState({ rnacentralDatabases: data, selectedDatabases: selectedDatabases });
      });
  }

}

export default withRouter(Search);
