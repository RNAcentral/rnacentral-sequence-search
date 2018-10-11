import routes from 'services/routes.jsx'

module.exports = {
  getFacets: function() {
    fetch(routes.facets, {method: "POST", })

  },


};
