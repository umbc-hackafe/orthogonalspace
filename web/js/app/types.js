function updateObj(a, b) {
    for (var attr in b) {
        if (b.hasOwnProperty(attr)) {
            a[attr] = b[attr];
         }
    }
}

window.orthogonalspace = {
    lobby: {
        LobbyShip: class {
            static updateFrom(obj) {
                if (this._instmap === undefined) this._instmap = {};

                if (obj.id in this._instmap) {
                    updateObj(this._instmap[obj.id], obj);
                } else {
                    this._instmap[obj.id] = obj;
                }
            }

            static updateTo(obj) {
                if (this._instmap === undefined) this._instmap = {};

                if (obj.id === undefined) return;

                if (obj.id in this._instmap) {
                    updateObj(obj, this._instmap[obj.id]);
                } else {
                    this._instmap[obj.id] = obj;
                }
            }

            static all() {
                if (this._instmap === undefined) this._instmap = {};
                return this._instmap;
            }

            constructor(id) {
                this.id = id;
                orthogonalspace.lobby.LobbyShip.updateTo(this);
            }

            register(wamp) {
                var self = this;
                wamp.subscribe('space.orthogonal.lobby.ship.ship' + this.id + '.updated',
                    function(res) {
                        var ship = jsonpickle.decode(res[0]);
                        console.log('updating to', ship);
                        updateObj(self, ship);
                    }
                );
            }

	        __setstate__(props) {
	            updateObj(this, props);
		        orthogonalspace.lobby.LobbyShip.updateFrom(this);
	        }
        }
    }
};
