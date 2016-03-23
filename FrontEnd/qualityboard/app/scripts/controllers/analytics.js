  'use strict';

/**
 * @ngdoc function
 * @name qualityboardApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the qualityboardApp
 */
angular.module('qualityboardApp')
  /*
  .factory('JiraIssues', function ($resource) {
    var url = 'https://jira.prosper.com/rest/api/2/search?jql=project+in+%28BOR%2C+MA%29+AND+fixVersion+%3D+12.08.15.Feature&maxResults=-1';
    return $resource(url, {}, {
      query: {
        method: 'GET',
        params: {},
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET', // POST, GET, OPTIONS, PUT, DELETE, HEAD', //, PATCH, DELETE',
          'Access-Control-Allow-Headers': 'Content-Type' //, X-PINGOTHER, Origin, X-Requested-With, Accept',
        }
      }
    });
  })
  */
  .controller('AnalyticsCtrl', function ($scope, $http) {
    NProgress.done();
  });
