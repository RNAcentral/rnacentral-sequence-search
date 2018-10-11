import React from 'react';


class Hit extends React.Component {
  render() {
    return (
      <li className="result">
        <div className="text-search-result">
          <h4>
            <a href="/rna/URS0000759B6D/9606">Homo sapiens miR-126 stem-loop</a>
          </h4>
          <small className="text-muted">URS0000759B6D_9606</small>
          <div className="small">
            <span>
              <em>Product:</em> <span>microRNA <span className="text-search-highlights">hsa-mir-126</span> precursor</span>
            </span>
          </div>
          <ul className="list-inline small ng-scope" ng-if="$ctrl.expertDbsObject">
            <li>
              85 nucleotides
            </li>
            <li>
              <i className="fa fa-check text-success" aria-hidden="true"></i> reference genome
            </li>
            <li>
            </li>
          </ul>
        </div>
      </li>
    )
  }
}

export default Hit;
