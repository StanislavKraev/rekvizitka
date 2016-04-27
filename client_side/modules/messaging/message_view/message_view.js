function x(Y) {
    "use strict";

    Y.MessageView = Backbone.View.extend({
        mailManager : null,
        mailListView : null,
        folderItems : [],
        initialize : function() {
            this.initFolderItems();
            this.mailManager = new Y.MailManager(this.folderItems, this.options.fetchUrl);
            this.mailListView = new Y.MailList({domElementName: this.options.rootDomElement});

            this.mailManager.bind('messagesFetched', this.onMessagesFetched, this);
            this.mailManager.getMails(this.options.defaultMailFolder, this.options.messagesOnPage);
        },
        onMessagesFetched : function(messages, folderId) {
            this.mailListView.setItems(messages);
            this.trigger('mailFolderItemsCountChanged', folderId, messages.length);
        },
        initFolderItems : function() {
            var i, folder, folderItem;

            this.folderItems = [];
            for (i = 0; i < this.options.folderList.length; i += 1) {
                folder = this.options.folderList[i];
                folderItem = new Y.CommonModels.FolderItem({
                    title : folder[0],
                    sid : folder[1],
                    count : folder[2]
                });
                this.folderItems.push(folderItem);
            }
        },
        onMailFolderChange : function(folderId) {
            this.mailManager.getMails(folderId, this.options.messagesOnPage);
        }
    });
}
