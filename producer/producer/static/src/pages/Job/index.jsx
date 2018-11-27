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
    this.displayStatusIcon = this.displayStatusIcon.bind(this);
  }

  getStatus() {
    fetch(routes.jobStatus(this.props.match.params.jobId))
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          window.clearTimeout(this.statusTimeout);
          this.props.history.push(`/result/${this.props.match.params.jobId}`);
        } else if (data.status === 'error') {
          window.clearTimeout(this.statusTimeout);
          this.props.history.push(`/error`);
        } else {
          this.statusTimeout = setTimeout(this.getStatus, 1000);
          this.setState(data);
        }
      });
  }

  displayStatusIcon(status) {
    if (status === 'success') return (<i className="icon icon-functional" style={{color: "green"}} data-icon="/"/>);
    else if (status === 'pending') return (<i className="icon icon-generic" data-icon="{"/>);
    else if (status === 'started') return (<i className="icon icon-functional spin" data-icon="s"/>);
    else if (status === 'error') return (<i className="icon icon-generic" style={{color: "red"}} data-icon="l"/>);
  }

  componentDidMount() {
    this.getStatus();
  }

  render() {
    return (
      <div className="row">
        <div className="col-lg-12">
          <div className="hpanel">
            <div className="panel-heading">
              <h1>Job { this.props.match.params.jobId } <small>{ this.displayStatusIcon(this.state.status) } { this.state.status }</small></h1>
            </div>
            <div className="panel-body">
              <table className="responsive-table">
                <thead>
                  <tr>
                    <th>Database</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  { this.state.chunks.map((chunk, index) => (
                    <tr key={index}>
                      <td>{ chunk.database }</td>
                      <td>{ this.displayStatusIcon(chunk.status) } { chunk.status }</td>
                    </tr>)) }
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Job;
