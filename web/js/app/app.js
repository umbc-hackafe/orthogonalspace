var orthogonal = angular.module('orthogonal', ["vxWamp", "ngRoute", "ngCookies", "orthogonalControllers"]);

orthogonal.config(function ($wampProvider) {
    $wampProvider.init({
        url: 'ws://' + window.location.hostname + ':8080/ws',
        realm: 'realm1'
    });
})

orthogonal.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
            when('/', {
                templateUrl: 'templates/home.html',
                controller: 'homeCtrl'
            }).
            when('/login', {
                templateUrl: 'templates/login.html',
                controller: 'loginCtrl'
            }).
            when('/logout', {
                templateUrl: 'templates/logout.html',
                controller: 'logoutCtrl',
            }).
            otherwise({
                redirectTo: '/'
            }
        );
    }
]);

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
