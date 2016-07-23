function updateObj(a, b) {
    for (var attr in b) {
        if (b.hasOwnProperty(attr)) {
            a[attr] = b[attr];
         }
    }
}

function registerUpdate(self, wamp, key) {
    wamp.subscribe(key + self.id + '.updated',
        function(res) {
            var newObj = jsonpickle.decode(res[0]);
            console.log('updating to', newObj);
            updateObj(self, newObj);
        }
    );
}


class UpdatableBase {
    prefix() {
        return '!';
    }

    wampKey() {
        return this.prefix() + this.id;
    }

    subscribe(suffix, callback) {
        this._wamp.subscribe(this.wampKey() + '.' + suffix, callback);
    }

    register(wamp) {
        this._wamp = wamp;
        registerUpdate(this, wamp, this.prefix());
    }

    call(suffix, args, kwargs) {
        return this._wamp.call(this.wampKey() + '.' + suffix, args, kwargs);
    }

    __setstate__(props) {
        updateObj(this, props);
    }
}

window.orthogonalspace = {
    lobby: {
        LobbyShip: class extends UpdatableBase {
            prefix() { return 'space.orthogonal.lobby.ship.ship'; }

            register(wamp) {
                super.register(wamp);
                this.subscribe('launched',
                    function(res) {
                        var data = jsonpickle.decode(res);
                        console.log(res);
                    }
                );
            }

            allReady() {
                for (var k in this.officers) {
                    if (!this.ready[k]) return false;
                }

                return true;
            }
        }
    },

    body: {
        Vector: class {

            __setstate__(props) {
                this.x = props.x;
                this.y = props.y;
                this.z = props.z;
            }
        }
    },

    ship: {
        Ship: class extends UpdatableBase {
            prefix() { return 'space.orthogonal.ship.ship'; }

            addThrust() {
                this.call('add_thrust', [10, 0, 0]).then(
                    function(res) {
                        console.log(res);
                    }
                )
            }

            decreaseThrust() {
                this.call('add_thrust', [-10, 0, 0]).then(
                    function(res) {
                        console.log(res);
                    }
                )
            }
        }
    },

    universe: {
        Universe: class extends UpdatableBase {
            prefix() { return 'space.orthogonal.universe.universe'; }
        }
    }
};
