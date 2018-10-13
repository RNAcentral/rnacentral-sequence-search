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
      .then(data => this.setState(data));
  }

  displayStatusIcon(status) {
    if (status === 'success') return (<i className="icon icon-functional" style={{color: "green"}} data-icon="/"/>);
    else if (status === 'started') return (<i className="icon icon-functional spin" data-icon="s"/>);
    else if (status === 'error') return (<i className="icon icon-generic" style={{color: "red"}} data-icon="l"/>);
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
              <h1>Job { this.props.match.params.jobId } { this.displayStatusIcon(this.state.status) }</h1>
            </div>
            <div className="panel-body">
              { this.state.chunks.map((chunk, index) => (<div key={index}> { chunk.database }: { this.displayStatusIcon(chunk.status) }</div>)) }
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Job;
