/*###############################################################################
##
##  Copyright (C) 2014, Tavendo GmbH and/or collaborators. All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright notice,
##     this list of conditions and the following disclaimer.
##
##  2. Redistributions in binary form must reproduce the above copyright notice,
##     this list of conditions and the following disclaimer in the documentation
##     and/or other materials provided with the distribution.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
##  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
##  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
##  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
##  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
##  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
##  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
##  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
##  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
##  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
##  POSSIBILITY OF SUCH DAMAGE.
##
###############################################################################
*/
// the URL of the WAMP Router (Crossbar.io)
//
var wsuri;
if (document.location.origin == "file://") {
   wsuri = "ws://127.0.0.1:8080/ws";

 } else {
    wsuri = (document.location.protocol === "http:" ? "ws:" : "wss:") + "//" +
                document.location.host + "/ws";
 }


 // the WAMP connection to the Router
 //
 var connection = new autobahn.Connection({
    url: wsuri,
    realm: "bridgesim"
 });


 // timers
 //
 var t1, t2;


 // fired when connection is established and session attached
 //
 connection.onopen = function (session, details) {

    console.log("Connected");

    // SUBSCRIBE to a topic and receive events
    //
    function on_counter (args) {
       var counter = args[0];
       console.log("on_counter() event received with counter " + counter);
    }
    session.subscribe('com.example.oncounter', on_counter).then(
       function (sub) {
          console.log('subscribed to topic');
       },
       function (err) {
          console.log('failed to subscribe to topic', err);
       }
    );


    // PUBLISH an event every second
    //
    t1 = setInterval(function () {

       session.publish('com.example.onhello', ['Hello from JavaScript (browser)']);
       console.log("published to topic 'com.example.onhello'");
    }, 1000);


    // REGISTER a procedure for remote calling
    //
    function mul2 (args) {
       var x = args[0];
       var y = args[1];
       console.log("mul2() called with " + x + " and " + y);
       return x * y;
    }
    session.register('com.example.mul2', mul2).then(
       function (reg) {
          console.log('procedure registered');
       },
       function (err) {
          console.log('failed to register procedure', err);
       }
    );


    // CALL a remote procedure every second
    //
    var x = 0;

    t2 = setInterval(function () {

       session.call('net.hackafe.bridgesim.echo', ["hello world" + x]).then(
          function (res) {
             console.log("echo() result:", res);
          },
          function (err) {
             console.log("echo() error:", err);
          }
       );

       x += 3;
    }, 1000);
 };


 // fired when connection was lost (or could not be established)
 //
 connection.onclose = function (reason, details) {
    console.log("Connection lost: " + reason);
    if (t1) {
       clearInterval(t1);
       t1 = null;
    }
    if (t2) {
       clearInterval(t2);
       t2 = null;
    }
 }


 // now actually open the connection
 //
 connection.open();
