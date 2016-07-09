var orthogonalControllers = angular.module('orthogonalControllers', []);

function updateShips(res, scope) {
    if (res != null) {
         var ships = jsonpickle.decode(res);
         scope.ships = {};

         for (var i in ships) {
             scope.ships[ships[i].id] = ships[i];
         }
     }
 }

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
                        $scope.ship = jsonpickle.decode(res);
                        $scope.ships[$scope.ship.id] = $scope.ship;
                    } else {
                        $scope.message = "Error: Could not create ship.";
                    }
                }
            );
        };

        $scope.chooseShip = function(ship) {
            $scope.ship = ship;
        };

        $scope.setShipName = function(name) {
            $wamp.call('space.orthogonal.lobby.ship.set_name', [jsonpickle.encode($scope.ship), jsonpickle.encode(name)]).then(
                function(res) {
                    if (res != null) {
                        //$scope.ship = jsonpickle.decode(res);
                    } else {
                        $scope.message = "Error: Could not update ship name.";
                    }
                }
            );

            $wamp.publish('space.orthogonal.lobby.ship.updated', [jsonpickle.encode($scope.ship)]);
        }

        $wamp.call('space.orthogonal.lobby.list_ships').then(
            function(res) {
                updateShips(res, $scope);
            }
        )

        $wamp.subscribe('space.orthogonal.lobby.event.ships_updated').then(
            function(res, ships) {
                updateShips(res, $scope);
            }
        );

        $wamp.subscribe('space.orthogonal.lobby.ship.updated',
            function(data) {
                var ship = jsonpickle.decode(data[0]);

                orthogonalspace.lobby.LobbyShip.updateFrom(ship);
            }
        ).then(function(res) {
            //
        });
    }
]);