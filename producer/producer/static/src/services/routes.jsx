module.exports = {
  'rnacentralDatabases': () => `/api/rnacentral-databases`,
  // 'facets':              () => `http://wp-p3s-f8:9050/ebisearch/ws/rest/rnacentral/seqtoolresults`,
  'submitJob':           () => `/api/submit-job`,
  'jobStatus':           (jobId) => `/api/job-status/${jobId}`,
  'jobResult':           (resultId) => `/api/job-result/${resultId}`,
  'facets':              (resultId) => `/api/facets/${resultId}`
};
