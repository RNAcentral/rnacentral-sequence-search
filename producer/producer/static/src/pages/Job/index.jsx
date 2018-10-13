import React from 'react';

import routes from 'services/routes.jsx';


class Job extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
        job_id: "",
        status: "",
        chunks: []
    };

    this.getStatus = this.getStatus.bind(this);
  }

  getStatus() {
    fetch(routes.jobStatus(this.props.match.params.jobId))
      .then(response => response.json())
      .then(data => this.setState(data));
  }

  componentDidMount() {
    this.setState({
      status: this.getStatus()
    })
  }

  render() {
    return (
      <div className="row">
        <div className="col-lg-12">
          <div className="hpanel">
            <div className="panel-heading">
              <h1>Job {this.props.match.params.jobId}</h1>
            </div>
            <div className="panel-body">
              {this.state.status}
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Job;
