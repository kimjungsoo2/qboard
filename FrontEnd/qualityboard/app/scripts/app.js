'use strict';

/**
 * @ngdoc overview
 * @name qualityboardApp
 * @description
 * # qualityboardApp
 *
 * Main module of the application.
 */
angular
  .module('qualityboardApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ui.bootstrap',
    'chart.js'
  ])
  .constant('domain', 'http://127.0.0.1:8000')
  //.constant('domain', 'http://10.121.184.79:81')
  /* a directive that will add class after the user leaves the text box. */
  .directive('showErrors', function() {
    return {
      restrict: 'A',
      require: '^form',
      link: function(scope, el, attrs, formCtrl) {
        // find the text box element, which has the 'name' attribute
        var inputEl = el[0].querySelector('[name]');

        // convert the native text box element to an angular element
        var inputNgEl = angular.element(inputEl);

        // get the name on the text box so we know the property to check on the form controller
        var inputName = inputNgEl.attr('name');

        // only apply the has-error class after the user leaves the text box
        inputNgEl.bind('blur', function() {
          el.toggleClass('has-error', formCtrl[inputName].$invalid);
        });
      }
    };
  })
  .filter('spaceless', function() {
    return function(input) {
      if (input) {
        input = input.replace(/\s+/g, '');
        input = input.replace(/[\/]/g, '');
        input = input.replace(/:/g, '');
        return input;
      }
    };
  })
  .filter('timestamp', function() {
    return function(input) {
      if (input) {
        var pos = input.indexOf('T');
        return input.substring(0, pos);
      }
    };
  })
  .filter('issuetype', function() {
    return function(text) {
      if (text) {
        switch (text) {
          case 'story':
            return 'Story';
          case 'bug':
            return 'Production Bug';
          case 'defect':
            return 'Defect';
          case 'task':
            return 'Task';
          case 'subtask':
            return 'Sub-Task';
          case 'test':
            return 'Test';
        }
      }
    };
  })
  .filter('keys', function() {
    return function(dict) {
      if (dict) {
        return Object.keys(dict);
      } else {
        return [];
      }
    };
  })
  .filter('exists', function() {
    return function(text) {
      if (text) {
        return text;
      } else {
        return 'Not Exists';
      }
    };
  })
  .filter('join', function() {
    return function(list) {
      return list.join(', ');
    };
  })
  .service('bootstrapService', function() {
    this.table = function(text) {
      if (text === 'PASS') {
        return 'table-success';
      } else if (text === 'FAIL') {
        return 'table-danger';
      } else if (text === 'BLOCKED') {
        return 'table-warning';
      } else {
        return 'table-default';
      }
    };

    this.panelTitle = function(text) {
      if (text === 'story') {
        return 'panel-title panel-title-primary';
      } else if (text === 'bug') {
        return 'panel-title panel-title-danger';
      } else if (text === 'defect') {
        return 'panel-title panel-title-warning';
      } else if (text === 'task' || text === 'subtask') {
        return 'panel-title panel-title-info';
      } else {
        return 'panel-title';
      }
    };

    this.label = function(text) {
      if (text === 'PASS' || text === 'Closed' || text === 'Accepted' || text === 'Verified' || text === 'Done') {
        return 'label label-success';
      }
      else if (text === 'Open' || text === 'Reopened' || text === 'Production Bug' || text === 'FAIL' ||
               text === 'To Do') {
        return 'label label-danger';
      }
      else if (text === 'In Progress' || text === 'Dev Complete' || text === 'Testing' || text === 'Code Review' ||
               text === 'Defect' || text === 'BLOCKED') {
        return 'label label-warning';
      }
      else if (text === 'Story') {
        return 'label label-primary';
      }
      else if (text === 'UNEXECUTED') {
        return 'label label-default';
      }
      else if (text === 'Task' || text === 'Sub-Task') {
        return 'label label-info';
      } else {
        return 'label label-default';
      }
    };

    this.text = function(text) {
      if (text === 'PASS' || text === 'Closed' || text === 'Accepted' || text === 'Verified' || text === 'Done') {
        return 'text text-success';
      }
      else if (text === 'Open' || text === 'Reopened' || text === 'Production Bug' || text === 'bug' || text === 'FAIL' ||
               text === 'To Do') {
        return 'text text-danger';
      }
      else if (text === 'In Progress' || text === 'Dev Complete' || text === 'Testing' || text === 'Code Review' ||
               text === 'Defect' || text === 'defect' || text === 'BLOCKED') {
        return 'text text-warning';
      }
      else if (text === 'Story' || text === 'story') {
        return 'text text-primary';
      }
      else if (text === 'Task' || text === 'task' || text === 'Sub-Task' || text === 'subtask') {
        return 'text text-info';
      }
      else {
        return 'text text-default';
      }
    };
  })
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
      })
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl'
      })
      .when('/overview', {
        templateUrl: 'views/overview.html',
        controller: 'OverviewCtrl'
      })
      .when('/reports', {
        templateUrl: 'views/reports.html',
        controller: 'ReportCtrl'
      })
      .when('/analytics', {
        templateUrl: 'views/analytics.html',
        controller: 'AnalyticsCtrl'
      })
      .when('/testutil', {
        templateUrl: 'views/testutil.html',
        controller: 'TestUtilCtrl'
      });
  })
  .controller('NavCtrl', function($scope, $rootScope, $location, $http, domain) {
    // initialize dropdown button
    /*$scope.selectedProj = {
      text: 'Select Project',
      key: null
    };*/

    $scope.curProject = 'Select Project';
    $rootScope.release = 'Select Release';

    NProgress.start();

    // load projects
    $http({
      method: 'GET',
      url: domain + '/project/'
    }).then(function successCallback(response) {
      $scope.projects = response.data;
    });

    // load fix versions
    $http({
          method: 'GET',
          url: domain + '/fixversion/'
        }).then(function successCallback(response) {
          $scope.releases = response.data;
        });

    NProgress.done();

    $scope.isActive = function(route) {
      return route === $location.path();
    };

    $scope.selectProj = function(name, key) {
      // save selected project key globally
      $rootScope.projectKey = key;
      $scope.curProject = name + ' (' + key + ')';

      if ($location.path() === '/overview') {
        $scope.getData();
      }

      if ($location.path() === '/reports') {
        $scope.getResults();
      }

      /*
      var borrowerTribe = ['BOR', 'VF', 'SPRK', 'GDS', 'PSA'];
      var ecosystemsTribe = ['EP'];
      var investorTribe = ['LEN'];
      var servicingTribe = ['RSER'];
      var tribe = '';

      if (borrowerTribe.indexOf(key) !== -1) {
        tribe = 'Borrower';
      } else if (ecosystemsTribe.indexOf(key) !== -1) {
        tribe = 'EcoSystems';
      } else if (investorTribe.indexOf(key) !== -1) {
        tribe = 'Investor';
      } else if (servicingTribe.indexOf(key) !== -1) {
        tribe = 'Servicing';
      }

      $http({
        method: 'GET',
        url: domain + '/fixversion/' + tribe
      }).then(function successCallback(response) {
        $scope.releases = response.data;

        // get Hotfix versions
        $http({
          method: 'GET',
          url: domain + '/fixversion/Hotfix'
        }).then(function successCallback(response) {
          $scope.releases = $scope.releases.concat(response.data);
        });

        NProgress.done();
      });
      */
    };

    // select fix version
    $scope.selectRelease = function(release) {
      $rootScope.release = release;

      if ($location.path() === '/overview') {
        $scope.getData();
      }

      if ($location.path() === '/reports') {
        $scope.getResults();
      }
    };


    /**
     * groupData from backend endpoint API
     */
    $scope.groupData = function(data, category) {
      $scope.groupedList = {};
      $rootScope.orderedGroupList = {};

      angular.forEach(data, function(obj) {
        var categorylist = [];

        if (Array.isArray(obj[category])) {
          angular.forEach(obj[category], function(v) {
            if (categorylist.indexOf(v.name) === -1) {
              categorylist.push(v.name);
            }
          });
        } else {
          if (obj[category]) {
            categorylist.push(obj[category]);
          } else {
            categorylist.push('');
          }
        }

        var issuetype = obj.issuetype;
        var status = obj.status;

        // grouping by category, then status
        angular.forEach(categorylist, function(category) {
          if (category in $scope.groupedList) {
            if (issuetype in $scope.groupedList[category]) {
              if (status in $scope.groupedList[category][issuetype]) {
                $scope.groupedList[category][issuetype][status].push(obj);
              } else {
                $scope.groupedList[category][issuetype][status] = [obj];
              }
            } else {
              $scope.groupedList[category][issuetype] = {};
              $scope.groupedList[category][issuetype][status] = [obj];
            }
          } else {
            $scope.groupedList[category] = {};
            $scope.groupedList[category][issuetype] = {};
            $scope.groupedList[category][issuetype][status] =[obj];
          }
        });
      });

      // sort by key
      var orderedKeys = Object.keys($scope.groupedList).sort();

      angular.forEach(orderedKeys, function(key) {
        $rootScope.orderedGroupList[key] = $scope.groupedList[key];

        // count total of each issue type
        angular.forEach($rootScope.orderedGroupList[key], function(list, issuetype) {
          var totalIssue = 0;

          angular.forEach(list, function(items, status) {
            totalIssue += items.length;
          });

          $rootScope.orderedGroupList[key][issuetype]['Total'] = totalIssue;
        });
      });

      console.log($rootScope.orderedGroupList);
    };


    /*
     * getData
     */
    $scope.getData = function() {
      NProgress.start();

      if ($rootScope.projectKey) {
        $http({
          method: 'GET',
          url: domain + '/cr/' + $rootScope.release + '/' + $rootScope.projectKey
        }).then(function successCallback(response) {
          if (response.data.length > 0) {
            // group by Epic
            $scope.groupData(response.data, 'priority');
          }
        });
      }

      NProgress.done();
    };


    /**
     * getData from backend endpoint API
     */
    $scope.getDataBACK = function(release) {
      $scope.alert = null;

      if ($rootScope.projectKey) {
        // initalization
        $rootScope.chartData = {};

        $rootScope.showList = [];

        $rootScope.crlist = {
          story: {},
          bug: {},
          defect: {},
          task: {},
          subtask: {}
        };

        $rootScope.status = {
          story: {
            total: 0,
            covered: 0
          },
          bug: {
            total: 0,
            covered: 0
          },
          defect: {
            total: 0,
            covered: 0
          },
          task: {
            total: 0,
            covered: 0
          },
          subtask: {
            total: 0,
            covered: 0
          },
          test: {
            Automated: [],
            Manual: []
          },
          result: {
            total: 0
          }
        };

        $rootScope.statusList = [];
        $rootScope.selectedStatus = [];
        $rootScope.executions = {};
        $rootScope.collapsed = {};

        // update with selected dropdown menu item
        $rootScope.selectedItem = release;

        // start progress
        NProgress.start();

        // load executions & JIRA tickets
        $http({
          method: 'GET',
          url: domain + '/execution/' + $rootScope.release + '/' + $rootScope.projectKey
        }).then(function successCallback(response) {
          // make a dictionary of executions
          angular.forEach(response.data, function(exec) {
            if (exec.testcase.key in $rootScope.executions) {
              $rootScope.executions[exec.testcase.key].push(exec);
            } else {
              $rootScope.executions[exec.testcase.key] = [exec];
            }
          });

          $http({
            method: 'GET',
            url: domain + '/cr/' + $rootScope.release + '/' + $rootScope.projectKey
          }).then(function successCallback(response) {
            // Get pulled date
            $rootScope.getDate = Date.now();

            angular.forEach(response.data, function(obj) {
              /*
              // generate collapsed dictionary
              $rootScope.collapsed[obj.jiraid] = {
                isCollapsed: true,
                label: 'more'
              };
              */

              // add test and count results
              obj.execlog = {};
              obj.execlog.total = 0;

              angular.forEach(obj.tests, function(test) {
                angular.forEach($rootScope.executions[test.key], function(exec) {
                  // count test results per test case
                  if (exec.status in obj.execlog) {
                    obj.execlog[exec.status] += 1;
                  } else {
                    obj.execlog[exec.status] = 1;
                  }

                  // count total
                  obj.execlog.total += 1;

                  // count overall test results
                  if (exec.status in $rootScope.status.result) {
                    $rootScope.status.result[exec.status].push(exec.execId);
                  } else {
                    $rootScope.status.result[exec.status] = [exec.execId];
                  }

                  $rootScope.status.result.total += 1;
                });

                // count total automated test cases
                if (test.exectype === 'Automated') {
                  if ($rootScope.status.test.Automated.indexOf(test.key) === -1) {
                    $rootScope.status.test.Automated.push(test.key);
                  }
                } else {
                  if ($rootScope.status.test.Manual.indexOf(test.key) === -1) {
                    $rootScope.status.test.Manual.push(test.key);
                  }
                }
              });

              // assign to each category
              switch (obj.issuetype) {
                case 'Defect':
                  // count status
                  if (obj.status in $rootScope.status.defect) {
                    $rootScope.status.defect[obj.status].push(obj.key);
                  } else {
                    $rootScope.status.defect[obj.status] = [obj.key];
                  }

                  $rootScope.status.defect.total += 1;

                  $rootScope.crlist.defect[obj.key] = obj;

                  // count covered defect
                  if (obj.tests.length > 0) {
                    $rootScope.status.defect.covered += 1;
                  }
                  break;
                case 'Story':
                  // count status
                  if (obj.status in $rootScope.status.story) {
                    $rootScope.status.story[obj.status].push(obj.key);
                  } else {
                    $rootScope.status.story[obj.status] = [obj.key];
                  }

                  $rootScope.status.story.total += 1;

                  $rootScope.crlist.story[obj.key] = obj;

                  // count covered story
                  if (obj.tests.length > 0) {
                    $rootScope.status.story.covered += 1;
                  }
                  break;
                case 'Production Bug':
                  // count status
                  if (obj.status in $rootScope.status.bug) {
                    $rootScope.status.bug[obj.status].push(obj.key);
                  } else {
                    $rootScope.status.bug[obj.status] = [obj.key];
                  }

                  $rootScope.status.bug.total += 1;

                  $rootScope.crlist.bug[obj.key] = obj;

                  // count covered production bug
                  if (obj.tests.length > 0) {
                    $rootScope.status.bug.covered += 1;
                  }
                  break;
                case 'Task':
                  // count status
                  if (obj.status in $rootScope.status.task) {
                    $rootScope.status.task[obj.status].push(obj.key);
                  } else {
                    $rootScope.status.task[obj.status] = [obj.key];
                  }

                  $rootScope.status.task.total += 1;

                  $rootScope.crlist.task[obj.key] = obj;

                  // count covered task
                  if (obj.tests.length > 0) {
                    $rootScope.status.task.covered += 1;
                  }
                  break;
                case 'Sub-Task':
                  // count status
                  if (obj.status in $rootScope.status.subtask) {
                    $rootScope.status.subtask[obj.status].push(obj.key);
                  } else {
                    $rootScope.status.subtask[obj.status] = [obj.key];
                  }

                  $rootScope.status.subtask.total += 1;

                  $rootScope.crlist.subtask[obj.key] = obj;

                  // count covered sub task
                  if (obj.tests.length > 0) {
                    $rootScope.status.subtask.covered += 1;
                  }
                  break;
              }
            });

            // manipulate data for charts
            angular.forEach($rootScope.status, function(value, type) {
              $rootScope.chartData[type] = {
                values: [value.covered, (value.total - value.covered)],
                labels: ['Test Covered', 'Uncovered'],
                colours: ['#5cb85c', '#5bc0de']
              };

              // get status list
              angular.forEach(value, function(v, k) {
                if (type !== 'test' && type !== 'result') {
                  if ($rootScope.statusList.indexOf(k) === -1 && k !== 'total' && k !== 'covered') {
                    $rootScope.statusList.push(k);
                  }
                }
              });
            });

            // sort status list
            $rootScope.statusList.sort();

            /*
            angular.forEach($rootScope.crlist.defect, function(defect) {
              angular.forEach(defect.issuelinks, function(issue) {
                if (issue.issuetype === 'Story') {
                  if (issue.key in $rootScope.crlist.story) {
                    angular.forEach(defect.tests, function(test) {
                      // get filtered obj array
                      var filtered = $rootScope.crlist.story[issue.key].tests.filter(function(obj) {
                        return obj.key === test.key;
                      });

                      // if filter array is empty, then push to tests list
                      if (filtered.length === 0) {
                        $rootScope.crlist.story[issue.key].tests.push(test);
                      }
                    });

                    if ($rootScope.crlist.story[issue.key].defects.indexOf(defect) === -1) {
                      $rootScope.crlist.story[issue.key].defects.push(defect);
                    }
                  }
                }
              });
            });
            */
            // complete the task
            NProgress.done();
          });
        });
      } else {
        $scope.alert = 'Please select project!';
      }
    };

    $scope.getResults = function() {
      $scope.alert = null;

      if ($rootScope.projectKey) {
        NProgress.done(true);

        // initialization
        $rootScope.chartParams = {};
        $rootScope.resultList = [];
        $rootScope.selectedResult = [];
        $rootScope.execution = {};

        // update with selected dropdown menu item
        // $rootScope.selectedItem = release;

        // start progress
        NProgress.start();
        $http({
          method: 'GET',
          url: domain + '/execution/' + $rootScope.release + '/' + $rootScope.projectKey
        }).then(function successCallback(response) {
          // Get pulled date
          $rootScope.getDate = Date.now();

          angular.forEach(response.data, function(exec) {
            try {
              if (exec.cycleName in $rootScope.execution) {
                if (exec.status in $rootScope.execution[exec.cycleName]) {
                  $rootScope.execution[exec.cycleName][exec.status].push(exec);
                } else {
                  $rootScope.execution[exec.cycleName][exec.status] = [exec];
                }
              } else {
                $rootScope.execution[exec.cycleName] = {};
                $rootScope.execution[exec.cycleName][exec.status] = [exec];
              }
            }
            catch (err) {
              console.log(err.message + '\n' + exec.cycleName + ', ' + exec.testcase);
              throw err;
            }
          });

          // calculate total of each cycle plan
          angular.forEach($rootScope.execution, function(value, key) {
            var total = 0;

            angular.forEach(value, function(execution) {
              total += execution.length;
            });

            $rootScope.execution[key].total = total;
          });

          /*
           * Draw donut chart
           */
          angular.forEach($rootScope.execution, function(value, planName) {
            $rootScope.chartParams[planName] = {
              values: [],
              labels: [],
              colours: []
            };
            angular.forEach($rootScope.execution[planName], function(list, result) {
              if (result !== 'total') {
                $rootScope.chartParams[planName].values.push(list.length);
                $rootScope.chartParams[planName].labels.push(result);

                switch (result) {
                  case 'PASS':
                    $rootScope.chartParams[planName].colours.push('#5cb85c');
                    break;
                  case 'FAIL':
                    $rootScope.chartParams[planName].colours.push('#d9534f');
                    break;
                  case 'BLOCKED':
                    $rootScope.chartParams[planName].colours.push('#f0ad4e');
                    break;
                  default:
                    $rootScope.chartParams[planName].colours.push('#777777');
                    break;
                }

                // add result to the list
                if ($rootScope.resultList.indexOf(result) === -1) {
                  $rootScope.resultList.push(result);
                }
              }
            });
          });

          // sort resultList
          $rootScope.resultList.sort();

          // set first tab active
          $rootScope.curTab = Object.keys($rootScope.execution)[0];

          NProgress.done();
        });
      } else {
        $scope.alert = 'Please select project!';
      }
    };
  });
