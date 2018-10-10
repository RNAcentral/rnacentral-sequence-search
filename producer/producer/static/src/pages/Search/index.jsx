import React from 'react';

class Search extends React.Component {
  render() {
    return (
      <div className="row">
        <div className="col-lg-12">
          <div className="hpanel">
            <div className="panel-heading">
              <h1>Submit an RNA sequence</h1>
            </div>
            <div className="panel-body">
              <form>
                <div className="jd_toolParameterBox">
                  <fieldset>
                    <legend>Enter your input RNA sequence:</legend>
                    <p>
                      <label htmlFor="sequence">
                        <a href="https://www.ebi.ac.uk/seqdb/confluence/display/THD/MUSCLE#MUSCLE-sequence" target="_help">Enter or paste</a>
                      </label>
                    </p>
                    <textarea cols="47" id="sequence" name="sequence" rows="7"></textarea>
                    <p>
                      Or upload a file:
                      <input id="upfile" name="upfile" type="file"/>
                      <label>
                        Use a <a href="#" id="exampleSeq">example sequence</a> | <a href="#" id="clearSequence">Clear sequence</a> | <a href="#" id="seeMoreExample">See more example inputs</a>
                      </label>
                    </p>
                  </fieldset>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Search;
