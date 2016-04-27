function x(Y) {
    "use strict";

    var MailManager;

    MailManager = function(folderList, fetchUrl) {
        this.initialize(folderList, fetchUrl);
    };

    _.extend(MailManager.prototype, Backbone.Events, {
        folders : [],
        fetchUrl : "",
        fetchXhr : null,
        initialize : function(folderList, fetchUrl) {
            var folderIndex,
                folderItem,
                folder;

            for (folderIndex = 0; folderIndex < folderList.length; folderIndex += 1) {
                folderItem = _.clone(folderList[folderIndex]);
                folder = new Y.MailModels.MailFolder({
                    sid : folderItem.get('sid'),
                    title : folderItem.get('title')
                });
                this.folders.push(folder);
            }

            this.fetchUrl = fetchUrl;
        },

        getFolder : function(folderId) {
            var i, folder;

            for (i = 0; i < this.folders.length; i += 1) {
                folder = this.folders[i];
                if (folder.get('sid') === folderId) {
                    return folder;
                }
            }

            return null;
        },

        getMails : function(folderId, count, startIndex) {
            var folder, folderVer, data;

            if (this.fetchXhr) {
                this.fetchXhr.abort();
                this.fetchXhr = null;
            }

            folder = this.getFolder(folderId);
            if (!folder) {
                Y.log('Incorrect folder id: ' + folderId, 'warn', 'messaging_application');
                return [];
            }
            folderVer = folder.version;

            data = {'folder' : folder.get('sid'),
                    'v' : folderVer,
                    'count' : count,
                    'startIndex' : startIndex};

            this.fetchXhr = $.ajax(this.fetchUrl, {
                success : this.onFetchSucceeded,
                error : this.onFetchFailed,
                type : 'POST',
                data : data,
                dataType : 'json',
                context : this,
                complete : this.onFetchComplete,
                beforeSend : function(jqXHR) { jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));}
            });

        },

        onFetchComplete : function() {
            this.fetchXhr = null;
        },
        onFetchSucceeded : function(result) {
            var i, item, items = result.messages, folderId = result.folder,
                folder = this.getFolder(folderId);


            if (!folder) {
                Y.log('Unknown folder Id: ' + folderId);
                return;
            }

            folder.clear();
            for (i = 0; i < items.length; i += 1) {
                item = new Y.MailModels.MailMessage(items[i], folder);
                folder.addMessage(item);
            }
            this.trigger('messagesFetched', folder.get('messages'), folder.get('sid'));
        },

        onFetchFailed : function() {
            Y.log('Mail fetch failed', 'warn', 'messaging_application');
        }
    });

    Y.MailManager = MailManager;
}
