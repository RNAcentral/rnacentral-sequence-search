import React from 'react';


class Hit extends React.Component {
  render() {
    return (
      <li className="result">
        <div className="text-search-result">
          <h4>
            <a href={`https://rnacentral.org/rna/${ this.props.result.rnacentral_id }`}>{ this.props.result.description }</a>
          </h4>
          <small className="text-muted">{ this.props.result.rnacentral_id }</small>
          <ul className="menu small">
            <li>{this.props.result.target_length} nucleotides</li>
            <li></li>
          </ul>
          <small>
            <a onClick={ this.props.onToggleAlignmentsCollapsed }>
              { this.props.alignmentsCollapsed ? <span><i className="icon icon-functional" data-icon="9" /> show alignments</span> : <span><i className="icon icon-functional" data-icon="8"/> hide alignments</span> }
            </a>
          </small>
          <div className="callout alignment alignment-collapsed">
            <table className="responsive-table">
              <thead>
                <tr>
                  <th>E-value</th>
                  <th>Identity</th>
                  <th>Query coverage</th>
                  <th>Target coverage</th>
                  <th>Gaps</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{ this.props.result.e_value }</td>
                  <td>{ this.props.result.identity }</td>
                  <td>{ this.props.result.query_coverage }</td>
                  <td>{ this.props.result.target_coverage }</td>
                  <td>{ this.props.result.gaps }</td>
                </tr>
              </tbody>
            </table>
            <p>{this.props.result.alignment}</p>
          </div>
        </div>
      </li>
    )
  }
}

export default Hit;
