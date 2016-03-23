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
  .controller('TestUtilCtrl', function($scope, $http, domain) {
    $scope.submit = function(request) {
      // start progress bar
      NProgress.start();

      // initialization
      $scope.accessToken = null;
      $scope.host = null;

      $http({
        method: 'POST',
        url: domain + '/email_bypass/' + request.env + '/' + request.email
      }).then(
        function successCallback(response) {
          $scope.textResp = response.data.message + '\n\n' +
                            response.status + ': ' + response.statusText + '\n' +
                            response.data.result + '\n\n' +
                            JSON.stringify(response.data.response);

          if (response.data.result === 'NOT VERIFIED') {
            // get activation key
            $scope.accessToken = response.data.response.activation_key;

            // get host for email verification
            if (request.env === 'qa32') {
              $scope.host = 'http://www.qa32.c1.dev/account/common/email_confirmation.aspx?code=';
            } else if (request.env === 'stg') {
              $scope.host = 'https://www.stg.circleone.com/account/common/email_confirmation.aspx?code=';
            } else if (request.env === 'qa20') {
              $scope.host = 'http://www.qa20.c1.dev/account/common/email_confirmation.aspx?code=';
            }
          }
        },
        function errorCallback(response) {
          $scope.textResp = response.data.message + '\n\n' +
                            response.status + ': ' + response.statusText + '\n' +
                            response.data.result + '\n\n' +
                            JSON.stringify(response.data.response);
        }
      );

      NProgress.done();
    };
  });
