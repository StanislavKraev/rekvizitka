function x(Y) {
    "use strict";

    var ChatDialogModel, ChatListDialogModel,
        ChatDialogMessageModel, CompanyEmployeeModel;

    ChatDialogModel = Backbone.Model.extend({
        defaults : {
            messages : null,
            isViewed : false,
            correspts : null,
            visavis : null,
            hasMore : false,
            id : null
        },
        initialize : function(params) {
            this.set('messages', this.get('messages') || []);
        },
        addMessage : function(userMessage) {
            if(this.getMessageById(userMessage.id)) {
                return false;
            }

            this.attributes['messages'].push(userMessage);
            return true;
        },
        addMessageInFront : function(userMessage) {
            if(this.getMessageById(userMessage.id)) {
                return false;
            }

            this.attributes['messages'].unshift(userMessage);
            return true;
        },
        getMessageById : function(msgId) {
            var i = null;
            $.each(this.get('messages'), function(id, val) {
                if (val.id === msgId) {
                    i = val;
                    return false;
                }
            });
            return i;
        },
        createListDialog : function() {
            return new Y.ChatListDialog({
                lastMessage : this.get('messages')[0],
                isViewed : this.get('isViewed'),
                correspts : this.get('correspts'),
                visavis : this.get('visavis'),
                id : this.get('id')
            });
        }
    });

    ChatListDialogModel = Backbone.Model.extend({
        defaults : {
            lastMessage : null,
            isViewed : false,
            correspts : null,
            visavis : null,
            id : null
        },
        createDialog : function() {
            return new Y.ChatDialog({
                messages : [ this.get('lastMessage') ],
                isViewed : this.get('isViewed'),
                correspts : this.get('correspts'),
                visavis : this.get('visavis'),
                id : this.get('id')
            });
        }
    });

    ChatDialogMessageModel = Backbone.Model.extend({
        defaults : {
            text : '',
            author : null,              // CompanyEmployee object
            date : null,
            id : null
        }
    });

    CompanyEmployeeModel = Backbone.Model.extend({
        defaults : {
            avatarCommentUrl : '',
            avatarDialogUrl : '',
            fullName : '',
            companyName : '',
            online : false,
            id : '',
            companyRekId : ''
        }
    });

    Y.ChatDialog = ChatDialogModel;
    Y.ChatListDialog = ChatListDialogModel;
    Y.ChatDialogMessage = ChatDialogMessageModel;
    Y.CompanyEmployee = CompanyEmployeeModel;
}
