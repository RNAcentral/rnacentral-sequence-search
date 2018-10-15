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
          <div className="callout alignment" data-closable>
            <button className="close-button" data-close>&times;</button>
            <p>{this.props.result.alignment}</p>
          </div>
        </div>
      </li>
    )
  }
}

export default Hit;
