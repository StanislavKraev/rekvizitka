function x(Y) {
    "use strict";

    var ChatDialogListView, ChatDialogListElementView,
        cdl_locales = Y.Locales['chat_dialog_list_view'];

    ChatDialogListView = Backbone.View.extend({
        template : Y.TemplateStore.load("chat_dialog_list_view_content"),
        container : null,
        dialogManager : Y.ChatDialogManager,
        locales : cdl_locales,
        pageElements : null,
        dialogIdElementMap : null,
        chatItemsPerPage : 4,
        chatCurrentPage : 1,

        initialize:function () {
            var headLine = (this.dialogManager.listDialogs.length > 0 ?
                String(this.dialogManager.listDialogs.length) + ' ' +
                    Y.utils.morph(this.locales.dialogsNumber, this.dialogManager.listDialogs.length, 'i') :
                "Нет диалогов");

            this.container = this.options.container;
            this.el = this.options.el;
            this.$el = $(this.el);
            this.pageElements = [];
            this.dialogIdElementMap = {};

            this.$el.html(this.template({
                headerDialogList: headLine
            }));

            this.initLayout();
            this.dialogManager.on("newMessage", this.onNewMessage, this);
            this.dialogManager.on("newDialog", this.onNewDialog, this);
            this.dialogManager.on("statusChange", this.onStatusChange, this);
            this.dialogManager.on("removeDialog", this.onRemoveDialog, this);
            this.dialogManager.on("markDialogRead", this.onMarkDialogRead, this);
        },

        onNewMessage:function (data) {
            var dialog = data.dialog,
                message = data.message,
                listDialog;
            listDialog = dialog.createListDialog();
            if (this.dialogIdElementMap.hasOwnProperty(dialog.get('id'))) {
                this.updateDialogItemView(listDialog);
            } else {
                console.warn('No such dialog - during attempt to insert message into dialog');
            }
        },

        onNewDialog:function (data) {
            var listDialog = data.dialog;
            if (this.dialogIdElementMap.hasOwnProperty(listDialog.get('id'))) {
                this.updateDialogItemView(listDialog);
            } else {
                this.insertNewDialog(listDialog);
            }
        },

        onStatusChange:function(data){
            var employee = data.employee, dialogId;
            dialogId = this.dialogManager.getDialogIdWithCorr(employee.get('id'));
            if (!dialogId) {
                return;
            }
            this.dialogIdElementMap[dialogId].changeStatus(employee.get('online'));
        },

        onRemoveDialog:function(data){
            $('#listelem_' + data.dialogID).remove();
            this.container.trigger('closeDynamicTab', data.dialogID);
            this.initLayout();
        },

        onMarkDialogRead : function(data) {
            var listDialog = data.dialogId,
                renewedDialog = this.dialogManager.dialogs[listDialog];
            if(renewedDialog) {
                renewedDialog.set('isViewed', true);
                this.dialogManager.addDialogToList(renewedDialog);
            }
            $('ul.company.dialogs #listelem_' + listDialog + ' .text-cloud').removeClass('unread');
        },

        afterShow : function() {
        },
        initLayout:function () {
            var that = this, headLine = (this.dialogManager.listDialogs.length > 0 ?
                String(this.dialogManager.listDialogs.length) + ' ' +
                    Y.utils.morph(this.locales.dialogsNumber, this.dialogManager.listDialogs.length, 'i') :
                "Нет диалогов");

            this.chatCurrentPage = Y.utils.getURLparam('p', 'number') || 1;

            this.$el.find('.headerDialogList').text(headLine);
            this.$el.find('ul.company.dialogs').off();
            this.$el.find('ul.company.dialogs').empty();
            this.drawListElements();
            this.$el.find('ul.company.dialogs').on('click', 'a', function (e) {
                Y.ApplicationRouter.navigate(e.currentTarget.pathname, { trigger : true });
                return false;
            });

            this.$el.find('ul.company.dialogs').on('click', 'li', function (e) {
                var corrId = e.currentTarget.id.split('_')[1];
                that.container.trigger('newTabOpen', {
                    dialogId:corrId,
                    callback:function () {
                        that.dialogManager.trigger('markDialogRead', { dialogId:corrId });
                    }
                });
                return false;
            });
            this.doPagination(this.getPageCount(), this.chatCurrentPage);
        },

        getPageCount:function(){
            return Math.ceil(this.dialogManager.listDialogs.length / this.chatItemsPerPage);
        },

        getRange:function(){
            var dialist = this.dialogManager.listDialogs;
            return dialist.slice(this.chatItemsPerPage * (this.chatCurrentPage-1),this.chatItemsPerPage * this.chatCurrentPage);
        },

        setData:function (params) {
            this.el = params.el;
            this.$el = $(this.el);
            this.container = params.container;
            this.initLayout();
        },

        drawListElements:function () {
            var chatListItem, dialogId, that = this;

            $.each(this.getRange(), function (iterId, iterListDialog) {
                dialogId = iterListDialog.get('id');
                $('ul.company.dialogs').append('<li id="listelem_' + dialogId + '"></li>');
                chatListItem = new Y.ChatDialogListElementView({
                    el:$('#listelem_' + dialogId),
                    model:iterListDialog,
                    container:that.container
                });
                chatListItem.show();
                that.pageElements.push(chatListItem);
                that.dialogIdElementMap[dialogId] = chatListItem;
            });
        },

        doPagination:function (quantity, current) {
            var html;

            if (quantity > 1) {
                if (!this.paginator) {
                    this.paginator = new Y.Paginator({
                        paginatorHolder:"paginator1", // id контейнера, куда ляжет пагинатор
                        pagesSpan:10, // число страниц, видимых одновременно
                        baseUrl:function (i) {
                            return '/chat/?p=' + i;
                        },
                        el:this.$el.find('.container-pagination')
                    });
                }

                html = this.paginator.render(quantity, current).el;

                this.paginator.bind('clickPaginatorPage', this.onPageChanged, this);

            } else {
                $('.container-pagination').empty();
            }
        },

        onPageChanged:function (pageId, url) {
            Y.ApplicationRouter.navigate(url, {trigger:true});
        },

        updateDialogItemView:function (listDialog) {
            var item = this.dialogIdElementMap[listDialog.get('id')], that = this;
            if (!item) {
                console.warn('Failed to update dialog ' + listDialog.get('id') + '. Not found.');
                return;
            }
            this.container.trigger('markDialogRead',
                { dialogId:listDialog.get('id'),
                    callback:function (viewFlag) {
                        listDialog.set('isViewed', viewFlag);
                        //item.setData(listDialog);
                        that.initLayout();
                    }
                });
        },

        insertNewDialog:function (listDialog) {
            var alreadyExists,
                listDialogId = listDialog.get('id');

            alreadyExists = this.dialogIdElementMap[listDialogId];
            if (alreadyExists) {
                console.warn('Dialog ' + listDialogId + ' already on the page.');
                return;
            }
            this.initLayout();
        }
    });

    ChatDialogListElementView = Backbone.View.extend({
        listContainer:null,
        template:Y.TemplateStore.load('chat_dialog_list_view_listelem'),
        locales : cdl_locales,
        dialogManager:Y.ChatDialogManager,

        initialize:function () {
            this.listContainer = this.options.container;
        },

        show:function () {
            return this.render();
        },

        changeStatus : function(online) {
            this.$el.find('.detail-status').removeClass('offline online').addClass(online ? 'online':'offline');
        },

        render:function () {
            var lastMessage, chatData, correspondent, lastMsgDate, that = this, msgTextCut;
            lastMessage = this.model.get('lastMessage');
            correspondent = this.model.get('visavis');
            lastMsgDate = lastMessage.get('date');
            msgTextCut = Y.utils.cutAndEscapeMultilineText(lastMessage.get('text'), 2, 50);
            chatData = {
                    corrName : correspondent.get('fullName'),
                    compName : correspondent.get('companyName'),
                    compNameCut : Y.utils.cutLongString(correspondent.get('companyName'), 16),
                    visavisAvatar : correspondent.get('avatarDialogUrl'),
                    authorIcon : lastMessage.get('author').get('avatarCommentUrl'),
                    authorName : lastMessage.get('author').get('fullName'),
                    net_status : correspondent.get('online'),
                    corrId : correspondent.get('id'),
                    loc_hide_dialog : this.locales['hideDialog'],
                    isUnread : !this.model.get('isViewed'),
                    lastMsgTime : Y.utils.makeShortDateString(lastMsgDate),
                    lastMsgText : lastMessage.get('text'),
                    lastMsgTextCut : msgTextCut,
                    company_url : '/' + correspondent.get('companyRekId') + '/profile/',
                    employee_url : '/' + correspondent.get('companyRekId') + '/profile/'
            };
            this.$el.html(this.template(chatData));
            if(chatData.net_status){
                this.$el.find('.detail-status').removeClass('offline').addClass('online');
            }

            this.$el.find('a.close').click(function (e) {
                var dialogID = e.target.parentElement.id.split('_')[1];
                that.dialogManager.removeDialog(dialogID);
                return false;
            });
            return this;
        },

        setData:function (listDialog) {
            this.model = listDialog;
            this.render();
        }
    });

    Y.ChatDialogListView = ChatDialogListView;
    Y.ChatDialogListElementView = ChatDialogListElementView;
}
