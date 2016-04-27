function x(Y) {
    "use strict";

    // Loading locale resources for current language
    var mod = this, FolderListView, FolderListItemsView;
    
    mod.resources = Y.Locales['folder-list'];

    //Views
    FolderListItemsView = Backbone.View.extend({
        tagName : 'div',
        selectedClassName : "selected",
        folderId : "",
        itemsCount : 0,
        template : Y.TemplateStore.load('folder-list_folder_list_item'),
        events : {
            "click a" : 'onFolderSelected'
        },

        initialize : function() {
            this.folderId = this.options.folderId;
            this.itemsCount = this.options.folderItemsCount;
        },

        onFolderSelected : function () {
            this.trigger('selectFolderItemEvent', this.folderId);
            return false;
        },

        render : function() {
            $(this.el).html(this.template({folder_name : mod.resources[this.options.folderName],
                                           folder_items_count : this.itemsCount,
                                           folder_id : this.folderId}));
            return this;
        },

        selectFolder : function() {
            $(this.el).addClass(this.selectedClassName);
        },

        unSelectFolder : function() {
            $(this.el).removeClass(this.selectedClassName);
        },
        setCount : function(count) {
            $(this.el).find('span.count').text(count);
        }
    });

    FolderListView = Backbone.View.extend({
        currentFolderId : "",
        folders : {},
        foldersArray : [],
        $folderList : null,
        template : Y.TemplateStore.load('folder-list_folder_list'),

        initialize : function() {
            this.$folderList = this.el;
            this.updateFolderListView();
        },

        updateFolderListView : function(){
            var i, listItemView,
                listSelf = this,
                selected,
                folderName,
                folderId,
                defaultFolderId;

            this.folderList = this.options.folderList;
            for (i = 0; i < this.folderList.length; i += 1) {
                if (this.folderList.hasOwnProperty(i)) {
                    folderName = this.folderList[i].get('title');
                    folderId = this.folderList[i].get('sid');
                    listItemView = new FolderListItemsView({folderName : folderName,
                                                            folderId : folderId,
                                                            folderItemsCount : this.folderList[i].get('count')});

                    this.folders[folderId] = listItemView;
                    this.foldersArray.push(listItemView);
                    this.$folderList.append(listItemView.render().el);
                    listItemView.bind('selectFolderItemEvent', listSelf.folderSelected, this);
                }
            }

            // todo: pass defaultMailFolder here from application
            if (this.options.defaultMailFolder) {
                defaultFolderId = this.options.defaultMailFolder;
                if (this.folders.hasOwnProperty(defaultFolderId)) {
                    this.currentFolderId = defaultFolderId;
                    listItemView = this.folders[this.currentFolderId];
                    listItemView.selectFolder();
                }
            }
            if (!this.currentFolderId.length && this.foldersArray.length) {
                this.foldersArray[0].selectFolder();
                this.currentFolderId = this.foldersArray[0].folderId;
            }
        },

        folderSelected : function(folderId){
            var folderIdIter;
            if (folderId === this.currentFolderId) {
                return;
            }
            for (folderIdIter in this.folders) {
                if (this.folders.hasOwnProperty(folderIdIter)) {
                    if (folderIdIter === folderId) {
                        this.folders[folderIdIter].selectFolder();
                        this.currentFolderId = folderIdIter;
                    } else {
                        this.folders[folderIdIter].unSelectFolder();
                    }
                }
            }
            this.trigger('folderSelected', this.currentFolderId);
        },

        setFolderItemsCount : function(folderId, count) {
            var folderIdIter;
            for (folderIdIter in this.folders) {
                if (this.folders.hasOwnProperty(folderIdIter)) {
                    if (folderIdIter === folderId) {
                        this.folders[folderIdIter].setCount(count);
                        return;
                    }
                }
            }
        }
    });

    Y.FolderList = FolderListView;
}
