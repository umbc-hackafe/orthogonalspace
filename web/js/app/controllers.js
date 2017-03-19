var orthogonalControllers = angular.module('orthogonalControllers', []);

function updateShips(res, scope, wamp) {
    if (res != null) {
         var ships = jsonpickle.decode(res);
         scope.ships = {};

         for (var i in ships) {
             scope.ships[ships[i].id] = ships[i];
             ships[i].register(wamp);
         }
     }
}

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

orthogonalControllers.controller('lobbyCtrl', ['$scope', '$wamp', '$cookies',
    function($scope, $wamp, $cookies) {
        $scope.selectedRoles = [];
        $scope.username = $cookies.get('username');

        $scope.createShip = function() {
            $wamp.call('space.orthogonal.lobby.ship.create').then(
                function(res) {
                    if (res != null) {
                        var ship = jsonpickle.decode(res);
                        $scope.ships[ship.id] = ship;
                        ship.register($wamp);
                        $scope.chooseShip(ship)
                    } else {
                        $scope.message = "Error: Could not create ship.";
                    }
                }
            );
        };

        $wamp.subscribe('space.orthogonal.lobby.ship.new',
            function(res) {
                var ship = jsonpickle.decode(res[0]);
                console.log('ship was createde', ship);
                ship.register($wamp);
                $scope.ships[ship.id] = ship;
            }
         )

        $scope.chooseShip = function(ship) {
            if ($scope.ship) {
                if ($scope.username in $scope.ship.officers) {
                    delete $scope.ship.officers[$scope.username];
                }
            }
            $scope.selectedRoles = [];

            $scope.ship = ship;

            if ($scope.username in $scope.ship.officers) {
                for (var k in $scope.ship.officers[$scope.username]) {
                    var role = $scope.ship.officers[$scope.username][k];
                    $scope.selectedRoles[role] = true;
                }
            } else {
                $scope.ship.officers[$scope.username] = [];
            }

            $scope.pickRole();

            $cookies.put('lastShip', $scope.ship.id);
        };

        $scope.pickRole = function(role) {
            var selected = [];
            for (var k in $scope.selectedRoles) {
                if ($scope.selectedRoles[k]) {
                    selected.push(k);
                }
            }

            $scope.ship.officers[$scope.username] = selected;
            $wamp.call('space.orthogonal.lobby.ship.ship' + $scope.ship.id + '.set_roles', [jsonpickle.encode($scope.username), selected]).then(
                function(res) {
                    console.log('set roles res', res);
                }
            )

            /*
            if (role in $scope.ship.officers[$scope.username]) {
                var index = $scope.ship.officers[$scope.username].indexOf(role);
                $scope.ship.officers[$scope.username].splice(index, 1);
            } else {
                $scope.ship.officers[$scope.username].push(role);
            }
            */
        };

        $scope.updateReady = function() {
            $wamp.call('space.orthogonal.lobby.ship.ship' + $scope.ship.id + '.set_ready', [jsonpickle.encode($scope.username), jsonpickle.encode($scope.ship.ready[$scope.username])]).then(
                function(res) {
                    console.log(res);
                }
            );
        };

        $scope.setShipName = function(name) {
            $wamp.call('space.orthogonal.lobby.ship.ship' + $scope.ship.id + '.set_name', [jsonpickle.encode(name)]).then(
                function(res) {
                    if (res != null) {
                        //$scope.ship = jsonpickle.decode(res);
                    } else {
                        $scope.message = "Error: Could not update ship name.";
                    }
                }
            );
        }

        $wamp.call('space.orthogonal.lobby.list_ships').then(
            function(res) {

                updateShips(res, $scope, $wamp);

                var lastShip = $cookies.get('lastShip');
                if (lastShip !== undefined) {
                    if ($scope.ships.hasOwnProperty(lastShip)) {
                        $scope.chooseShip($scope.ships[lastShip]);
                    }
                }
            }
        );

        $wamp.subscribe('space.orthogonal.lobby.event.ships_updated',
            function(datas) {
                res = jsonpickle.decode(datas[0]);
                updateShips(res, $scope, $wamp);
            }
        ).then(function(res){});

        $scope.launch = function() {
            // TODO: Don't hardcode the universe ID to 0
            $wamp.call('space.orthogonal.lobby.ship.ship' + $scope.ship.id + '.launch', [0]).then(
                function(res) {
                    console.log(res);
                }
            );
        }

        $wamp.subscribe('space.orthogonal.lobby.ship.launched',
            function(datas) {
                res = jsonpickle.decode(datas);
                console.log(res);
            }
        )
    }
]);

setupHelmController(orthogonalControllers);
setupMapController(orthogonalControllers);