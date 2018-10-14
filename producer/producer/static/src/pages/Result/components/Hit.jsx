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
          <div className="small">
            <span>
              <em>Product:</em> <span>microRNA <span className="text-search-highlights">hsa-mir-126</span> precursor</span>
            </span>
          </div>
          <ul className="menu small">
            <li>{this.props.result.target_length} nucleotides</li>
            <li></li>
          </ul>
        </div>
      </li>
    )
  }
}

export default Hit;
