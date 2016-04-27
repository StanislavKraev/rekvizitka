function x(Y) {
    "use strict";

    var _socket = null, ServerChannelManager, SocketProxy = function(){}, _connected = false;

    _.extend(SocketProxy.prototype, {
        emit : function(name, data) {
            if (!_connected) {
                return;
            }
            if (_socket) {
                return _socket.emit(name, data);
            }
        }
    });

    ServerChannelManager = {
        subscribers : {},
        operationTypeList : {'new_message' : 2,
                             'status_change' : 3,

                             'dlg_marked_read' : 5},
        subscribe : function(operationType, callback, name, thisPtr) {
            var newSocketProxy, that = this;
            if (!this.operationTypeList.hasOwnProperty(operationType) || this.subscribers.hasOwnProperty(name)) {
                return null;
            }
            if (!_socket) {
                _socket = io.connect('/dchat', {'resource':'dchat', 'connect timeout' : 25000});
                _socket.on('connect', function() {
                    _connected = true;
                });
                _socket.on('disconnect', function() {
                    _connected = false;
                });
                _socket.on('operation', function(data) {
                    var opType = data.operation_type, subscriberName, subscriber, newCts = data.new_cts;
                    Y.utils.setCookie('cts', newCts, {expires:3600});
                    for (subscriberName in that.subscribers) {
                        if (that.subscribers.hasOwnProperty(subscriberName)) {
                            subscriber = that.subscribers[subscriberName];
                            if (opType === subscriber.opType) {
                                that.notifySubscriber(subscriber, data);
                            }
                        }
                    }
                });
                _socket.on('operations', function(data) {
                    var newCts = data.new_cts, opType;
                    Y.utils.setCookie('cts', newCts, {expires:3600});
                    $.each(data.ops, function(id, iterOper) {
                        opType = iterOper.operation_type;
                        $.each(that.subscribers, function(subscriberId, iterSubscriber) {
                            if (iterSubscriber.opType === opType) {
                                that.notifySubscriber(iterSubscriber, data);
                            }
                        });
                    });
                });
            }
            newSocketProxy = new SocketProxy();
            this.subscribers[name] = {'socket' : newSocketProxy,
                                      'callback' : callback,
                                      'opType' : this.operationTypeList[operationType],
                                      'thisPtr' : thisPtr};

            return newSocketProxy;
        },

        notifySubscriber : function(subscriber, data) {
            setTimeout(function(){
                subscriber.callback.call(subscriber.thisPtr, data);
            }, 1);
        },

        unsubscribe : function(name) {
            if (this.subscribers.hasOwnProperty(name)) {
                delete this.subscribers[name];
            }
            if (!this.subscribers.length && _socket) {
                _socket.close();
            }
        }
    };
    _.extend(ServerChannelManager, Backbone.Events);

    Y.ServerChannelManager = ServerChannelManager;
}
