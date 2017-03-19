function setupHelmController(orthogonalControllers) {
    orthogonalControllers.controller('helmCtrl', ['$scope', '$wamp', '$cookies', '$location', 'entityService',
        function($scope, $wamp, $cookies, $location, entityService) {
            $wamp.subscribe('space.orthogonal.game.tick',
                function(payload) {
                    var data = jsonpickle.decode(payload);
                    console.log('!NYI! Got tick data', data);
                }
            ).then(function(res){});

            var shipId = $cookies.get('lastShip');

            if (shipId !== undefined) {
                $wamp.call('space.orthogonal.lobby.ship.ship' + shipId + '.get').then(
                    function(res) {
                        if (res != null) {
                            var lobbyShip = jsonpickle.decode(res);
                            if (lobbyShip.locked) {
                                $scope.ship = lobbyShip.entity_ship;
                                $scope.ship.register($wamp, entityService);
                                entityService.registerEntity($scope.ship);
                            } else {
                                console.error("Ship selected is not embarked!");
                                $location.path('/');
                            }
                        } else {
                            console.error("Got null result for space.orthogonal.lobby.ship.shipX.get");
                        }
                    }
                );
            }
        }
    ]);
}
