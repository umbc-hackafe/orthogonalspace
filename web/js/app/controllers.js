var orthogonalControllers = angular.module('orthogonalControllers', []);

orthogonalControllers.controller('homeCtrl', ['$scope', '$wamp',
    function($scope, $wamp) {
    }
]);

orthogonalControllers.controller('loginCtrl', ['$scope', '$wamp', '$location', '$cookies',
    function($scope, $wamp, $location, $cookies) {
        $scope.login = function() {
            $wamp.call('com.login', [$scope.username, $scope.password]).then(
                function (res) {
                    if (res != null) {
                        $cookies.put('websession', res);
                        $cookies.put('username', $scope.username);
                        $location.path("/");
                    } else {
                        $scope.errorMessage = "Login failed, please try again.";
                    }
                }
            );
        };
        $scope.add_user = function() {
            $wamp.call('com.add_user', [$scope.username, $scope.password]).then(
                function () {
                    $scope.errorMessage = "User Created. Please Log In.";
                }
            );
        };
    }
]);

orthogonalControllers.controller('logoutCtrl', ['$scope', '$wamp', '$cookies',
    function($scope, $wamp, $cookies) {
        $wamp.call('com.logout', [$cookies.get('username'), $cookies.get('websession')]).then(
            function (res) {
                if (res) {
                    $cookies.remove('username');
                    $cookies.remove('websession');
                    $scope.message = "Logged out successfully.";
                } else {
                    $scope.message = "Error: Could not log out.";
                }
            }
        );
    }
]);

orthogonalControllers.controller('lobbyCtrl', ['$scope', '$wamp',
    function($scope, $wamp) {
        $scope.createShip = function() {
            $wamp.call('space.orthogonal.lobby.ship.create').then(
                function(res) {
                    if (res != null) {
                        console.log(res);
                    } else {
                        $scope.message = "Error: Could not create ship.";
                    }
                }
            )
        };
    }
]);