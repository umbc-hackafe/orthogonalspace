var ON = 0;
var TOP = 1;
var RIGHT = 2;
var BOTTOM = 3;
var LEFT = 4;
var TOP_RIGHT = 5;
var BOTTOM_RIGHT = 6;
var BOTTOM_LEFT = 7;
var TOP_LEFT = 8;

class OverheadMap {

    constructor(height, width) {
        this.height = height;
        this.width = width;

        this.center = [0, 0, 0];
        this.zoom = 1;
    }

    zoomFactor() {
        return Math.pow(2, this.zoom);
    }

    bounds() {
        return [
            this.center[0] - this.zoomFactor() * this.width / 2,
            this.center[1] - this.zoomFactor() * this.height / 2,
            this.center[0] + this.zoomFactor() * this.width / 2,
            this.center[1] + this.zoomFactor() * this.height / 2,
        ];
    }

    getWorldCoordinates(mapX, mapY) {
        return [
            this.center[0] + (mapX - this.width / 2) * this.zoomFactor(),
            this.center[1] - (mapY - this.height / 2) * this.zoomFactor()
        ];
    }

    toMapSpace(x, y, z) {
        return [
            (x - this.center[0]) / this.zoomFactor() + this.width / 2,
            (y - this.center[0]) / this.zoomFactor() + this.height / 2
        ];
    }

    mapEdge(x, y) {
        var bounds = this.bounds();
        console.log(bounds);
        var left = x < bounds[0];
        var right = x > bounds[2];
        var top = y > bounds[3]
        var bottom = y < bounds[1];

        if (!left && !right && !top && !left) {
            return ON;
        } else if (top && right) {
            return TOP_RIGHT;
        } else if (bottom && right) {
            return BOTTOM_RIGHT;
        } else if (bottom && left) {
            return BOTTOM_LEFT;
        } else if (top && left) {
            return TOP_LEFT;
        } else if (top) {
            return TOP;
        } else if (right) {
            return RIGHT;
        } else if (bottom) {
            return BOTTOM;
        } else if (left) {
            return LEFT;
        }
    }

    drawOffTriangle(x, y) {
    }

    drawShip(ctx, ship) {
        console.log("Drawing ship")
        console.log("World coordinates", ship.position);
        var coords = this.toMapSpace(ship.position.x, ship.position.y, ship.position.z);

        ctx.fillStyle = '#003366';
        ctx.beginPath();
        ctx.arc(coords[0], coords[1], 5, 0, 2*Math.PI);
        ctx.fill();
    }

    redraw(canvas, objects) {
        var ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, this.width, this.height);

        for (var k in objects) {
            var ent = objects[k];

            var edge = this.mapEdge(ent.position.x, ent.position.y);
            if (edge == ON) {
                console.log("On the map!");
                this.drawShip(ctx, ent);
            } else {
                console.log("off map to direction", edge);

            }
        }

        console.log("yup");
    }
}

function setupMapController(orthogonalControllers) {
    orthogonalControllers.controller('mapCtrl', ['$scope', '$interval', 'entityService',
        function($scope, $interval, entityService) {
            console.log("it works?");

            console.log($scope);

            $scope.map = new OverheadMap(500, 500);

            $scope.zoomIn = function() {
                console.log("zooming in");
                if ($scope.map.zoom > 1) {
                    $scope.map.zoom -= 1;
                }
            }


            $scope.zoomOut = function() {
                console.log("zooming out");
                $scope.map.zoom += 1;
            }

            $scope.redraw = function(entities) {
                $scope.map.redraw(document.getElementById('overhead-map-canvas'), entities);
            }

            $scope.$on('entitiesUpdated', function(event, entities) {
                $scope.redraw(entities);
            });
        }
    ]);
}
