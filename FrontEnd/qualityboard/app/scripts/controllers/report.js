'use strict';

/**
 * @ngdoc controller
 * @name Report
 *
 * @description
 * _Please update the description and dependencies._
 *
 * @requires $scope
 * */
angular.module('qualityboardApp')
  .controller('ReportCtrl', function($scope, $rootScope, $http, domain, bootstrapService) {
    // tab selection hander
    $scope.selectTab = function(text) {
      $scope.curTab = text;
    };

    // is nav tab active
    $scope.isTabActive = function(text) {
      return $scope.curTab === text;
    };

    // set bootstrap label
    $scope.setLabel = function(text) {
      return bootstrapService.label(text);
    };

    /* click item */
    $scope.clickItem = function(item) {
      var index = $scope.selectedResult.indexOf(item);

      if (index === -1) {
        $scope.selectedResult.push(item);
      } else {
        $scope.selectedResult.splice(index, 1);
      }
    };

    /**
     * display
     */
    $scope.display = function(key) {
      /*
      if ($scope.showList.length > 0) {
        if ($scope.showList.indexOf(key) !== -1) {
          return 'collapse in';
        } else {
          return 'collapse out';
        }
      } else {
        return 'collapse in';
      }
      */
      if ($scope.selectedResult.length > 0) {
        if ($scope.selectedResult.indexOf(key) !== -1) {
          return 'collapse in';
        } else {
          return 'collapse out';
        }
      }
    };
  });
