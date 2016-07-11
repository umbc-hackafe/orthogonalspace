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

window.orthogonalspace = {
    lobby: {
        LobbyShip: class {
            register(wamp) {
                registerUpdate(this, wamp, 'space.orthogonal.lobby.ship.ship')
            }

	        __setstate__(props) {
	            updateObj(this, props);
	        }

	        allReady() {
	            console.log('all ready?');
                for (var k in this.officers) {
                    if (!this.ready[k]) return false;
                }

                console.log('yes');
                return true;
	        }
        }
    },

    ship: {
        Ship: class {
            register(wamp) {
                registerUpdate(this, wamp, 'space.orthogonal.ship.ship');
            }

            __setstate__(props) {
                updateObj(this, props);
            }
        }
    },

    universe: {
        Universe: class {
            register(wamp) {
                registerUpdate(this, wamp, 'space.orthogonal.universe.universe');
            }

            __setstate__(props) {
                updateObj(this, props);
            }
        }
    }
};
