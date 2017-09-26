window.Firechannel = (function() {
  /**
   * Firechannels are used to connect to Firebase.
   *
   * @param token The auth token from the server.
   */
  var Firechannel = function(token) {
    var segments = token.split(".");
    var params = JSON.parse(atob(segments[1]));

    this.channelId = params.uid;
    this.token = token;
  };

  /**
   * Open a socket.
   *
   * @param handler An optional object with handlers for Socket callbacks.
   * @param onError An optional error handler.
   * @return Socket
   */
  Firechannel.prototype.open = function(handler, onError) {
    firebase.auth().signInWithCustomToken(this.token).catch(onError || function(err) {
      console.log("Error: " + err.code);
      console.error(err.message);
    });

    var ref = firebase.database().ref("firechannels/" + this.channelId);
    var socket = new Socket(ref, handler || {});
    return socket;
  };

  /**
   * Sockets receive data in real time form Firebase.
   *
   * @param ref A Firebase Reference.
   * @param handler An optional object with handlers for the callbacks.
   */
  var Socket = function(ref, handler) {
    this.ref = ref;
    this.handler = handler;

    ref.on("value", function(ref) {
      try {
        var data = ref.val();
        if (data === null) {
          return;
        }

        var message = data.message;

        handler.onmessage ? handler.onmessage(message) : this.onmessage(message);
      } catch (e) {
        handler.onerror ? handler.onerror(e) : this.onerror(e);
      }
    }.bind(this));

    handler.onopen ? handler.onopen() : this.onopen();
  };

  /**
   * Callend when the socket is ready to receive messages.
   */
  Socket.prototype.onopen = function() {};

  /**
   * Called when the socket receives a message.
   *
   * @param data The data sent from the server.
   */
  Socket.prototype.onmessage = function(data) {};

  /**
   * Called when an error occurs on the socket.
   *
   * @param err An object with a `code` field and a `message` field.
   */
  Socket.prototype.onerror = function(err) {};

  /**
   * Called when the socket is closed.
   */
  Socket.prototype.onclose = function() {};

  /**
   * Close the socket.
   */
  Socket.prototype.close = function() {
    if (this.ref) {
      this.ref.off();
      this.handler.onclose ? this.handler.onclose() : this.onclose();
    }
  };

  return Firechannel;
})();
