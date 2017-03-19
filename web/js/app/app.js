var orthogonal = angular.module('orthogonal', ["vxWamp", "ngRoute", "ngCookies", "orthogonalControllers"]);

orthogonal.config(function ($wampProvider) {
    $wampProvider.init({
        url: 'ws://' + window.location.hostname + ':8080/ws',
        realm: 'orthogonalspace'
    });
})

orthogonal.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
            when('/', {
                templateUrl: 'templates/lobby.html',
                controller: 'lobbyCtrl'
            }).
            when('/login', {
                templateUrl: 'templates/login.html',
                controller: 'loginCtrl'
            }).
            when('/logout', {
                templateUrl: 'templates/logout.html',
                controller: 'logoutCtrl',
            }).
            when('/helm', {
                templateUrl: 'templates/helm.html',
                controller: 'helmCtrl',
            }).
            otherwise({
                redirectTo: '/'
            }
        );
    }
]);

orthogonal.factory('entityService', function($rootScope) {
    var entityService = {};

    entityService.entities = [];

    entityService.registerEntity = function(entity) {
        entityService.entities.push(entity);
    }

    entityService.broadcastEntities = function() {
        $rootScope.$broadcast('entitiesUpdated', entityService.entities);
    }

    entityService.updateEntities = function(entities) {
        entityService.entities = entities;
        entityService.broadcastEntities();
    }

    entityService.entityUpdated = function(entity) {
        entityService.broadcastEntities();
    }

    return entityService;
});

orthogonal.run(function($cookies, $location, $wamp, $rootScope) {
    $rootScope.$on("$routeChangeStart", function(event, next, current) {
        if (next.templateUrl === "templates/login.html") {
        } else {
            if ($cookies.get('websession') == null) {
                $location.path("/login");
            } else {
                $wamp.call('com.sessioncheck', [$cookies.get('username'), $cookies.get('websession')]).then(
                    function(res) {
                        if (!res) {
                            $location.path("/login");
                        }
                    }
                );
            }
        }
    });
});

orthogonal.run(function($wamp) {
  $wamp.open();
});
