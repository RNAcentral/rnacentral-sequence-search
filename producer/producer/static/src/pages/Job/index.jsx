import React from 'react';

class Job extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
        status: "",
        chunks: []
    };

    this.getStatus = this.getStatus.bind(this);
  }

  getStatus() {
    fetch(routes.jobStatus(this.props.jobId))
      .then( (response) => {
        return response.json()
      })
      .then( (json) => {
        return json; // setState in here with your ajax request**strong text**
      });
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
              <h1>Home</h1>
            </div>
            <div className="panel-body">
              <p>Content of search page.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Job;
