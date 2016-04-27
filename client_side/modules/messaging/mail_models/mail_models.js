function x(Y) {
    "use strict";

    Y.MailModels = {
        MailMessage : Backbone.Model.extend({
            defaults : {
                content : "",
                subject : "",
                author : null,
                recipients : [],
                sentDate : new Date()
            }
        }),
        MailFolder : Backbone.Model.extend({
            defaults : {
                sid : "",       // our internal id, not Backbone's one
                messages : [],  // List of MailMessage objects
                title : "",
                version : 0
            },
            addMessages : function(messageList) {
                this.attributes.messages = this.attributes.messages.concat(_.clone(messageList));
            },
            addMessage : function(message) {
                this.attributes.messages.push(message);
            },
            clear : function() {
                this.attributes.messages = [];
            }
        }),
        Contact : Backbone.Model.extend({
            defaults : {
                address : "",
                fullName : "",
                avatar : ""
            }
        })
    };
}
