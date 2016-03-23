'use strict';

/**
 * @ngdoc function
 * @name qualityboardApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the qualityboardApp
 */
angular.module('qualityboardApp')
  .controller('AboutCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
