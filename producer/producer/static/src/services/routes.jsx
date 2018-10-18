module.exports = {
  rnacentralDatabases: () => `/api/rnacentral-databases`,
  submitJob:           () => `/api/submit-job`,
  jobStatus:           (jobId) => `/api/job-status/${jobId}`,
  jobResult:           (resultId) => `/api/job-result/${resultId}`,
  facets:              (resultId) => `/api/facets/${resultId}`,
  facetsSearch:        (resultId, query, page, page_size) => `/api/facets/${resultId}?query=${query}&page=${page}&page_size=${page_size}`
  // ebiSearch:           (jobId, query, fields, facetcount, facetfields, pagesize, start) =>
  //   `http://wp-p3s-f8:9050/ebisearch/ws/rest/rnacentral/seqtoolresults` +
  //   `?query=${query}` +
  //   `&format=json&fields=${fields}` +
  //   `&facetcount=${facetcount}` +
  //   `&facetfields=${facetfields}` +
  //   `&size=${pagesize}` +
  //   `&start=${start}`,
};
