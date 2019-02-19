import React from 'react';


class Documentation extends React.Component {
  onIframeLoad() {
    let iframe = document.getElementById('swagger-iframe');
    let style = document.createElement('style');

    style.textContent = `
      .swagger-section #header {
        display: none;
      }
      
      .swagger-section #api_info {
        display: none;
      }
      
      .swagger-section #message-bar {
        display: none;
      }
    `;

    iframe.contentDocument.head.appendChild(style);
  }

  render() {
    return (
      <div className="row">
        <div className="col-lg-12">
          <div className="hpanel">
            <div className="panel-heading">
              <h1>Documentation</h1>
            </div>
            <div className="panel-body">
              <div className="responsive-embed">
                <iframe src="/api/doc" frameBorder="0" onLoad={this.onIframeLoad} id="swagger-iframe"></iframe>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Documentation;
