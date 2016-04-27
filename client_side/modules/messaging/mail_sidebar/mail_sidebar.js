function x(Y) {
    "use strict";

    Y.MailSidebarView = Backbone.View.extend({
        folderList : null,
        folderItems : [],
        template : Y.TemplateStore.load('mail_sidebar_sidebar'),
        initialize : function() {
            this.initFolderItems();
            this.sid = this.options.sid;
        },
        render : function() {
            this.$el.append(this.template());
            this.folderList = new Y.FolderList({folderList : this.folderItems,
                defaultMailFolder : this.options.defaultMailFolder,
                el : this.$el.find('.folder_list')
            });
            this.folderList.bind('folderSelected', this.setFolder, this);
            return this;
        },
        setFolder : function(folderId){
            this.trigger('folderSelected', folderId);
        },
        setFolderItemsCount : function(folderId, count) {
            this.folderList.setFolderItemsCount(folderId, count);
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
        show : function() {
            this.$el.show();
        },
        hide : function() {
            this.$el.hide();
        }
    });
}