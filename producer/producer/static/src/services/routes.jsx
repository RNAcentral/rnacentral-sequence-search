module.exports = {
  rnacentralDatabases: () => `/api/rnacentral-databases`,
  submitJob:           () => `/api/submit-job`,
  jobStatus:           (jobId) => `/api/job-status/${jobId}`,
  jobResult:           (resultId) => `/api/job-result/${resultId}`,
  facets:              (resultId) => `/api/facets/${resultId}`
  // ebiSearch:           (jobId, query, fields, facetcount, facetfields, pagesize, start) =>
  //   `http://wp-p3s-f8:9050/ebisearch/ws/rest/rnacentral/seqtoolresults` +
  //   `?query=${query}` +
  //   `&format=json&fields=${fields}` +
  //   `&facetcount=${facetcount}` +
  //   `&facetfields=${facetfields}` +
  //   `&size=${pagesize}` +
  //   `&start=${start}`,
};
