function x(Y) {
    "use strict";

    var ChatDialogManager = {
        dialogs:{}, // открытые вкладки диалогов: полный набор сообщений
        listDialogs:[], // краткая информация о диалогах - только для списка и уже отсортированные по дате
        correspts:{},
        version:null,
        isDialogListInitialised : false,
        isDialogInitialized : {},
        socket:null,

        brandName:'',
        employeeName:'',
        emplid:'',

        /* Events                                                               */

        /* -------------------------------------------------------------------- */
        /*      newMessage                                                      */
        /*  params:                                                             */
        /*      {'dialog' : dialog object,                                      */
        /*       'message' : message object}                                    */

        /* -------------------------------------------------------------------- */
        /*      newDialog                                                       */
        /*  params:                                                             */
        /*      {'dialog' : list dialog object}                                 */

        /* -------------------------------------------------------------------- */
        /*      statusChange                                                    */
        /*  params:                                                             */
        /*      {'employee' : object with net status}                           */

        /* -------------------------------------------------------------------- */
        /*      unreadMessageCountChanged                                       */
        /*  params:                                                             */
        /*      unreadDialogsNewCount                                           */


        /* Notifications from the server */

        onNewMessage : function (data) {
            if(data.hasOwnProperty('dialog')) {
                this.newMessageInDialog(data);
            }
        },

        onStatusChange:function (data) {
            var employeeID = data.employee, employee,
                online = data.online;

            employee = this.correspts[employeeID];

            if(employee){
                employee.set('online',online);
                this.trigger("statusChange", {
                    'employee':employee
                });
            }
        },

        onDialogMarkedAsRead : function(data) {
            var dialogId = data.dialog;
            if(this.hasListDialog(dialogId)) {
                this.trigger('markDialogRead', { 'dialogId' : dialogId });
                this.notifyAboutUnreadDialogs();
            }
        },

        /* Common API */

        connectToServer:function () {
            this.socket = Y.ServerChannelManager.subscribe('new_message', this.onNewMessage, 'cdm_new_msg', this);
            Y.ServerChannelManager.subscribe('status_change', this.onStatusChange, 'cdm_status_change', this);

            Y.ServerChannelManager.subscribe('dlg_marked_read', this.onDialogMarkedAsRead, 'cdm_dlg_marked_read', this);
        },

        disconnectFromServer:function () {
            Y.ServerChannelManager.unsubscribe('cdm_new_msg');
            this.socket = null;
        },

        initFromDialogList:function (callback) {
            var url = '/chat/list/i/', that = this;
            if (this.isDialogListInitialised) {
                callback();
            } else {
                if (Y.Chat_init && Y.Chat_init.hasOwnProperty('dialogs')) {
                    that.initManagerTail(callback);
                } else {
                    $.ajax(url, {
                        success:function (data) {
                            if (data.error) {
                                Y.Informer.show("Не удалось получить данные с сервера", 10);
                            } else {
                                Y.Chat_init = data;
                                that.initManagerTail(callback);
                            }
                        },
                        error:function () {
                            Y.Informer.show("Не удалось получить данные с сервера", 10);
                        },
                        type:'GET',
                        dataType:'json'
                    });
                }
            }
        },

        initFromDialog : function (callback, dialogId) {
            var url = '/chat/dialog/' + dialogId + '/i/', that = this;

            if(!this.dialogs.hasOwnProperty(dialogId)) {
                if (Y.Chat_init && ((Y.Chat_init.hasOwnProperty('dialog') && Y.Chat_init.dialog.id === dialogId) ||
                    (Y.Chat_init.hasOwnProperty('dialogs') && Y.Chat_init.dialogs.hasOwnProperty(dialogId)))) {
                    that.initManagerTail(callback);
                } else {
                    $.ajax(url, {
                        success:function (data) {
                            if (data.error) {
                                Y.Informer.show("Не удалось получить данные с сервера", 10);
                            } else {
                                Y.Chat_init = data;
                                that.initManagerTail(callback);
                            }
                        },
                        error:function () {
                            Y.Informer.show("Не удалось получить данные с сервера", 10);
                        },
                        type:'GET',
                        dataType:'json'
                    });
                }
            } else {
                callback();
            }
        },

        createDialog : function (companionId, callback) {
            var that = this;
            $.ajax('/chat/create/' + companionId + '/', {
                success:function (data) {
                    if (data.error) {
                        callback(null);
                        return;
                    }

                    that.brandName = data.brandname || "";
                    that.emplid = data.emplid || "";
                    that.employeeName = "Администратор";
                    that.company_logo = data.company_logo || '/media/i/default_company_page.png';
                    that.rekid = data.rekid || '';

                    that.getDialog(data.dialog.id, callback);
                },
                error:function () {
                    callback(null);
                },
                type:'POST',
                data:{},
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });

        },

        getDialog : function (dialogId, callback) {
            if (this.dialogs.hasOwnProperty(dialogId)) {
                callback(this.dialogs[dialogId]);
                return;
            }
            this.loadDialog(dialogId, callback);
        },

        loadDialog : function (dialogId, callback) {
            var that = this;
            $.ajax('/chat/dialog/' + dialogId + '/i/', {
                success : function (data) {
                    var newDialog, correspondent, i, listDialog, corrPack = {};
                    if (data.error) {
                        callback(null);
                    } else {
                        if (data.hasOwnProperty('correspts') && data.hasOwnProperty('dialog')) {
                            for (i in data.correspts) {
                                if (data.correspts.hasOwnProperty(i)) {
                                    correspondent = data.correspts[i];
                                    that.addCorrespondent(i, correspondent);
                                }
                            }

                            corrPack[data.dialog.correspt] = that.correspts[data.dialog.correspt];
                            corrPack[data.emplid] = that.correspts[data.emplid];
                            newDialog = new Y.ChatDialog({ id:data.dialog.id,
                                isViewed : data.dialog.isViewed || false,
                                correspts : corrPack,
                                visavis : that.correspts[data.dialog.correspt],
                                hasMore : data.dialog.has_more });

                            if (data.dialog.messages && data.dialog.messages.length) {
                                $.each(data.dialog.messages, function(id, message) {
                                    var newMessage = new Y.ChatDialogMessage({text : message.text,
                                                                              author : that.correspts[message.author],
                                                                              date : Y.utils.stringToDate(message.date),
                                                                              id : message.id });
                                    newDialog.addMessage(newMessage);
                                });
                            }

                            that.dialogs[data.dialog.id] = newDialog;
                            listDialog = that.addDialogToList(newDialog);
                            that.trigger('newDialog', {'dialog':listDialog});

                            callback(newDialog);
                        } else {
                            callback(null);
                        }
                    }
                },
                error : function () {
                    callback(null);
                },
                type : 'GET',
                data : {},
                dataType : 'json',
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        newMessageInDialog : function(data) {
            var dialogId = data.dialog,
                dialog,
                message,
                that = this,
                listDialog;

            message = new Y.ChatDialogMessage({'text' : data.text || '',
                'author' : this.correspts[data.author],
                'date' :Y.utils.stringToDate(data.date),
                'id' : data.message_id});

            dialog = this.dialogs[dialogId];

            if(!dialog) {
                this.loadDialog(dialogId, function (dialog) {
                    if (!dialog) {
                        console.warn('Failed to get data for dialog ' + dialogId + ' during processing CDM.newMessageInDialog()');
                        return;
                    }
                    dialog.set('isViewed', data.author === that.emplid);
                    that.trigger("newMessage", {
                        'dialog' : dialog,
                        'message' : message
                    });
                    that.notifyAboutUnreadDialogs();
                });
            } else {
                dialog.addMessageInFront(message);
                dialog.set('isViewed', data.author === this.emplid);

                listDialog = this.addDialogToList(dialog);
                this.trigger('newDialog', {
                    'dialog' : listDialog
                });

                this.trigger("newMessage", {
                    'dialog' : dialog,
                    'message' : message
                });

                this.notifyAboutUnreadDialogs();
            }
        },

        loadOldMessages : function(dialogId, callback) {
            var that = this, currLength = this.dialogs[dialogId].get('messages').length;
            $.ajax('/chat/mm/' + dialogId + '/', {
                success : function(data) {
                    var currDialog = that.dialogs[dialogId];
                    if (data.error) {
                        console.warn("Error from chat/mm: " + data.error);
                        callback(null);
                    } else {
                        $.each(data.messages, function(id, message) {
                            var newMessage = new Y.ChatDialogMessage({text : message.text,
                                author : that.correspts[message.author],
                                date : Y.utils.stringToDate(message.date),
                                id : message.id });
                            currDialog.addMessage(newMessage);
                        });
                        currDialog.set('hasMore', data.has_more || false);
                        callback(data.messages.length);
                    }
                },
                error : function() {
                    callback(null);
                },
                type : 'GET',
                data : { 's' : currLength,
                         'n' : 10 },
                dataType : 'json',
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        addMessage:function (message, dialogId) {
            this.socket.emit('add_dlg_msg', {'text':message, 'dialog_id':dialogId});
        },

        getDialogIdWithCorr:function (corrId) {
            var foundDialog;
            $.each(this.listDialogs, function(id, iterDialog) {
                if (iterDialog.get('visavis').get('id') === corrId) {
                    foundDialog = iterDialog;
                    return false;
                }
            });
            return foundDialog ? foundDialog.get('id') : null;
        },

        getCorrFromDialogId:function (dialogId) {
            var foundCorr = null;
            $.each(this.dialogs, function (iterDialogId, iterDialog) {
                if (iterDialog.get('id') === dialogId) {
                    foundCorr = iterDialog.get('visavis');
                    return false;
                }
            });
            return foundCorr;
        },

        hasListDialog:function (dialogId) {
            var found = false;
            $.each(this.listDialogs, function (id, iterDialog) {
                if (iterDialog.get('id') === dialogId) {
                    found = true;
                    return false;
                }
            });
            return found;
        },

        getListDialog:function (dialogId) {
            var found = null;
            $.each(this.listDialogs, function (id, iterDialog) {
                if (iterDialog.get('id') === dialogId) {
                    found = iterDialog;
                    return false;
                }
            });
            return found;
        },

        getIndexListDialog:function (dialogId) {
            var found = -1;
            $.each(this.listDialogs, function (id, iterDialog) {
                if (iterDialog.get('id') === dialogId) {
                    found = id;
                    return false;
                }
            });
            return found;
        },

        markDialogAsRead : function(dialogId) {
            if (this.socket) {
                this.socket.emit('check_dialog_viewed', {'dialog_id' : dialogId});
            }
        },

        removeDialog:function(dialogID){
            var url = '/chat/delete/' + dialogID + '/', that = this;
            $.ajax(url, {
                success:function (data) {
                    var listIndex;
                    listIndex= that.getIndexListDialog(dialogID);
                    if(listIndex >= 0) {
                        that.listDialogs.splice(listIndex,1);
                    }
                    delete that.dialogs[dialogID];

                    that.trigger("removeDialog", {
                        'dialogID':dialogID
                    });
                },
                error:function () {

                },
                type:'GET',
                dataType:'json'
            });
        },

        notifyAboutUnreadDialogs : function() {
            var count = 0;
            $.each(this.listDialogs, function(itId, itListDialog) {
                if (!itListDialog.get('isViewed')) {
                    count += 1;
                }
            });
            this.trigger('unreadMessageCountChanged', count);
        },

        /* Internals */

        initManagerTail:function (callback) {
            var dialog, that = this, dialogId;

            this.brandName = Y.Chat_init.brandname || "Некая компания";
            this.emplid = Y.Chat_init.emplid;

            if (Y.Chat_init.hasOwnProperty('correspts')) {
                $.each(Y.Chat_init.correspts, function (id, corrData) {
                    that.addCorrespondent(id, corrData);
                });
            }

            this.employeeName = (this.correspts.hasOwnProperty(this.emplid) ?
                this.correspts[this.emplid].get('fullName') :
                "(Администратор)");

            if (Y.Chat_init.hasOwnProperty('dialogs')) {
                if (this.isDialogListInitialised) {
                    console.warn('Dialog manager already initialized with dialog list');
                    callback();
                    return;
                }
                this.isDialogListInitialised = true;
                $.each(Y.Chat_init.dialogs, function (id, dialogData) {
                    that.addDialogData(dialogData);
                });
            } else if (Y.Chat_init.hasOwnProperty('dialog')) {
                dialogId = Y.Chat_init.dialog.id;
                if(!this.isDialogInitialized.hasOwnProperty(dialogId) ||
                    !this.isDialogInitialized[dialogId]) {
                    dialog = Y.Chat_init['dialog'];
                    this.addDialogData(dialog);
                    this.isDialogInitialized[dialogId] = true;
                }
            }
            callback();
        },

        addDialogData:function (dialogData) {
            var lastMessageData,
                dialogMessage,
                listDialog,
                fullDialog,
                corrPack = {},
                that = this;

            corrPack[dialogData.correspt] = that.correspts[dialogData.correspt];
            corrPack[this.emplid] = that.correspts[this.emplid];

            if (dialogData.hasOwnProperty('messages')) {
                fullDialog = new Y.ChatDialog({ id:dialogData.id,
                    isViewed:dialogData.isViewed || false,
                    correspts:corrPack,
                    visavis:this.correspts[dialogData.correspt],
                    hasMore : dialogData.has_more || false });

                $.each(dialogData.messages, function (id, messageData) {
                    var newMessage = new Y.ChatDialogMessage({
                        text : messageData.text,
                        author : that.correspts[messageData.author],
                        date : Y.utils.stringToDate(messageData.date),
                        id : messageData.id
                    });
                    fullDialog.addMessage(newMessage);
                });

                this.dialogs[dialogData.id] = fullDialog;
            }

            lastMessageData = dialogData['lastmessage'];
            if (lastMessageData && !this.hasListDialog(dialogData.id)) {
                dialogMessage = new Y.ChatDialogMessage({
                    text : lastMessageData.text,
                    author : this.correspts[lastMessageData.correspt],
                    date :Y.utils.stringToDate(lastMessageData.time),
                    id : lastMessageData.id
                });

                listDialog = new Y.ChatListDialog({
                    lastMessage:dialogMessage,
                    isViewed:dialogData.isViewed,
                    correspt:corrPack,
                    visavis:this.correspts[dialogData.correspt],
                    id:dialogData.id
                });

                this.listDialogs.push(listDialog);
                this.sortListDialogs();
            }
        },

        addCorrespondent:function (id, corrData) {
            this.correspts[id] = new Y.CompanyEmployee({
                id:id,
                avatarCommentUrl:corrData.avatarurl || '/media/i/default_man_comment.png',
                avatarDialogUrl:corrData.avatarurl || '/media/i/default_man_dialog.png',
                fullName:corrData.fullname || '',
                companyName:corrData.companyname || '',
                companyRekId : corrData.company_rek_id || '',
                online:corrData.online || false
            });
        },

        addDialogToList:function (fullDialog) {
            var listIndex = this.findDialogInList(fullDialog),
                dlgExtract = fullDialog.createListDialog();

            if (listIndex === null) {
                this.listDialogs.push(dlgExtract);
            } else {
                this.listDialogs[listIndex] = dlgExtract;
            }
            this.sortListDialogs();
            return dlgExtract;
        },

        sortListDialogs:function () {
            this.listDialogs.sort(function (d1, d2) {
                if(typeof(d1) === 'undefined' || typeof(d1.get('lastMessage')) === 'undefined') {
                    return 1;
                }
                if(typeof(d2) === 'undefined' || typeof(d2.get('lastMessage')) === 'undefined') {
                    return -1;
                }
                return d2.get('lastMessage').get('date') - d1.get('lastMessage').get('date');
            });
        },

        findDialogInList:function (dialogObject) {
            var foundId = null;
            $.each(this.listDialogs, function (id, iterDialog) {
                if (iterDialog.get('id') === dialogObject.get('id')) {
                    foundId = id;
                    return false;
                }
            });
            return foundId;
        }
    };
    _.extend(ChatDialogManager, Backbone.Events);

    Y.ChatDialogManager = ChatDialogManager;
}
