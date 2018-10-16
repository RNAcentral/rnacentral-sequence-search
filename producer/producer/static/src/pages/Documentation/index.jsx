import React from 'react';


class Documentation extends React.Component {
  render() {
    return (
      <div className="row">
        <div className="col-lg-12">
          <div className="hpanel">
            <div className="panel-heading">
              <h1>Documentation</h1>
            </div>
            <div className="panel-body">
              <p>
                <a href="/api/doc">API documentation</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Documentation;
