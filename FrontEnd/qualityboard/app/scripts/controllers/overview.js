  'use strict';

/**
 * @ngdoc function
 * @name qualityboardApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the qualityboardApp
 */
angular.module('qualityboardApp')
  .controller('OverviewCtrl', function ($scope, $rootScope, $http, domain, bootstrapService) {
    NProgress.done(true);

    /**
     * isDefectExist
     * check if the defect is mentioned in other stories
     */
    $scope.isDefectExist = function(defect) {
      var isExist = false;

      if (defect.issuelinks) {
        for (var i = 0; i < defect.issuelinks.length; i++) {
          if (defect.issuelinks[i].issuetype === 'Story' && defect.issuelinks[i].key in $scope.crlist.story) {
            isExist = true;
            break;
          }
        }
      }

      return isExist;
    };

    /**
     * getGroupItemClass
     * it returns the bootstrap group item class based on the status
     */
    /*
    $scope.getGroupItemClass = function(key) {
      var status;

      if (key in $scope.results) {
        status = $scope.results[key].status;
      } else if (key in $scope.crlist.defect) {
        status = $scope.crlist.defect[key].status;
      }

      if (status === 'Verified' || status === 'Closed' || status === 'PASS') {
        return 'list-group-item list-group-item-success';
      }
      else if (status === 'Open' || status === 'Reopened' || status === 'FAIL') {
        return 'list-group-item list-group-item-danger';
      }
      else if (status === 'In Progress' || status === 'Dev Complete' || status === 'Testing' || status === 'Code Review' || status === 'BLOCKED') {
        return 'list-group-item list-group-item-warning';
      }
      else {
        return 'list-group-item';
      }
    };*/

    // set bootstrap label
    $scope.setLabel = function(text) {
      return bootstrapService.label(text);
    };

    // set bootstrap label
    $scope.setText = function(text) {
      return bootstrapService.text(text);
    };

    // set bootstrap panel-title
    $scope.setPanelTitle = function(text) {
      return bootstrapService.panelTitle(text);
    };

    // set bootstrap table tr or td
    $scope.setTable = function(text) {
      return bootstrapService.table(text);
    };

    /**
     * isAutomated
     * returns glyphicon if execution type is Automated.
     */
    $scope.isAutomated = function(exectype) {
      if (exectype === 'Automated') {
        return 'glyphicon glyphicon-flash';
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
      if ($scope.selectedStatus.length > 0) {
        if ($scope.selectedStatus.indexOf(key) !== -1) {
          return 'collapse in';
        } else {
          return 'collapse out';
        }
      }
    };

    /**
     * toggling collapse
     */
    $scope.collapse = function(idx) {
      $scope.collapsed[idx].isCollapsed = !$scope.collapsed[idx].isCollapsed;

      if ($scope.collapsed[idx].isCollapsed) {
        $scope.collapsed[idx].label = 'more';
      } else {
        $scope.collapsed[idx].label = 'less';
      }
    };

    $scope.actionCollapse = function(idx) {
      return $scope.collapsed[idx].isCollapsed;
    };

    /*
    click item
    */
    $scope.clickItem = function(item) {
      var index = $scope.selectedStatus.indexOf(item);

      if (index === -1) {
        $scope.selectedStatus.push(item);
      } else {
        $scope.selectedStatus.splice(index, 1);
      }
    };

    /**
     * showOnly
     */
    $scope.showOnly = function(list, type) {
      $scope.showList = [];

      if (type) {
        $scope.showList.push(type);
      }

      angular.forEach(list, function(key) {
        // add to the list
        if ($scope.showList.indexOf(key) === -1) {
          $scope.showList.push(key);
        }

        /*
        // add to associated story to the list
        if (key in $scope.crlist.defect) {
          angular.forEach($scope.crlist.defect[key].issuelinks, function(issue) {
            if (issue.issuetype === 'Story' || issue.issuetype === 'Production Bug') {
              if ($scope.showList.indexOf(issue.key) === -1) {
                $scope.showList.push(issue.key);
              }
            }
          });
        }
        */
      });
    };
  });
