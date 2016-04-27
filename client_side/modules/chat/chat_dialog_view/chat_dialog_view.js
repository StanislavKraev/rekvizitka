function x(Y) {
    "use strict";

    var ChatDialogView, ChatDialogMessageView,
        msgTemplate = Y.TemplateStore.load('chat_dialog_view_messageitem'),
        chatDlgTemplate = Y.TemplateStore.load('chat_dialog_view_content');

    ChatDialogView = Backbone.View.extend({
        container : null,
        dialogId : '',
        dialogManager : Y.ChatDialogManager,
        correspts : null,
        locales : Y.Locales['chat_dialog_view'],
        template : chatDlgTemplate,
        justOpened : true,

        initialize : function() {
            var that = this;
            this.container = this.options.container;
            this.el = this.options.el;
            this.$el = $(this.el);
            this.dialogId = this.options.dialogId;
            this.dialogManager.getDialog(this.dialogId, function(dialog) {
                if (!dialog) {
                    Y.Informer.show("Не удалось открыть диалог", 10);
                    return;
                }
                that.model = dialog;
                that.correspts = that.model.get('correspts');
                that.initLayout();
                that.justOpened = false;
            });
            this.dialogManager.on("newMessage", this.onNewMessage, this);
            this.dialogManager.on("statusChange", this.onStatusChange, this);
        },

        activate : function() {
            console.warn("just activated tab");
        },
        onNewMessage : function(data) {
            var msgblock, dlgmsgelem, sendVisible;

            if (this.dialogId === data.dialog.get('id')) {
                sendVisible = this.sendButtonIsVisible();
                msgblock = this.$el.find('ul');
                msgblock.append('<li id="dlgelem_' + data.message.get('id') + '"></li>');
                dlgmsgelem = new Y.ChatDialogMessageView({
                    model : new Y.ChatDialogMessage({ id : data.message.get('id'),
                                                      author : data.message.get('author'),
                                                      text : data.message.get('text'),
                                                      date : data.message.get('date') }),
                    el : $('#dlgelem_' + data.message.get('id'))
                });
                dlgmsgelem.show();
                if(data.message.get('author').get('id') !== this.model.get('visavis').get('id')) {
                    this.scrollToSendForm();
                } else {
                    if(sendVisible > 0) {
                        this.reboundFromPageBottom(sendVisible);
                    }
                }
            }
        },
        sendButtonIsVisible : function() {
            var lowerWindowBound = $(window).height() + $(window).scrollTop(),
                messageBlockTop = $('.write-message-block').offset().top;
            return (lowerWindowBound > messageBlockTop ? this.getPageLowerBound() : -1);
        },
        onStatusChange : function(data) {
            if(data.employee.get('id') === this.model.get('visavis').get('id')) {
                this.updateStatus();
            }
        },
        updateStatus : function() {
            var statusCls = this.model.get('visavis').get('online') ? 'online' : 'offline';
            this.$el.find('.correspondent .icon.net-status').removeClass('online offline').addClass(statusCls);
        },
        afterShow : function() {
        },
        setData : function(params) {
            var that = this;
            this.el = params.el;
            this.$el = $(this.el);
            this.container = params.container;
            this.dialogId = params.dialogId;

            this.dialogManager.getDialog(this.dialogId, function(dialog) {
                if (!dialog) {
                    Y.Informer.show("Не удалось открыть диалог", 10);
                    return;
                }
                that.model = dialog;
                that.correspts = that.model.get('correspts');
                that.initLayout();
            });
        },
        initLayout : function() {
            var dlgparams, that = this;
            this.$el.empty();
            dlgparams = {
                loc_view_dialog : this.locales.viewDialog,
                loc_send : this.locales.send,
                loc_enter_message : this.locales.enterMessage,
                loc_show_previous : this.locales.showPrevious,
                corrname : this.model.get('visavis').get('fullName'),
                bnamecut : Y.utils.cutLongString(this.model.get('visavis').get('companyName'), 30),
                bname : this.model.get('visavis').get('companyName'),
                mini_logo_url : this.model.get('visavis').get('avatarCommentUrl') || '/media/i/default_man_comment.png',
                dialog_logo_url : this.model.get('visavis').get('avatarDialogUrl') || '/media/i/default_man_dialog.png',
                company_url : '/' + this.model.get('visavis').get('companyRekId') + '/profile/',
                employee_url : '/' + this.model.get('visavis').get('companyRekId') + '/profile/'
            };
            this.$el.append(this.template(dlgparams));
            this.drawMessageList();
            this.updateStatus();

            function _sendMessage() {
                var message = $.trim(that.$el.find("#chat_message_ta").val());
                if (message.length) {
                    that.dialogManager.addMessage(message, that.dialogId);
                    that.$el.find("#chat_message_ta").val('');
                }
                return false;
            }
            this.$el.find("#send_message_btn").click(_sendMessage);
            this.$el.find("table.write-message-block").keypress(function (eventObj) {
                var code = eventObj.keyCode || eventObj.which;
                if (((code === 13) || (code === 10)) && (eventObj.ctrlKey === true)) {
                    _sendMessage();
                    return false;
                }
            });
            this.prependShowMoreLine();
            this.dialogManager.markDialogAsRead(this.dialogId);

            this.$el.find('#chat_message_ta').elastic();

            if(this.model.get('isViewed') && !this.justOpened) {
                this.afterShow = function() {};
            } else {
                this.afterShow = function() {
                    that.scrollToSendForm();
                };
            }
        },
        drawMessageList : function() {
            var msgBlock = this.$el.find('ul'), i,
                dlgMessages = this.model.get('messages');
            for(i = 0; i < dlgMessages.length; i += 1) {
                this.prependDialogMessage(msgBlock, dlgMessages[i]);
            }
        },
        prependDialogMessage : function(msgBlock, msgObj) {
            var dlgMsgElem;
            msgBlock.prepend('<li id="dlgelem_' + msgObj.get('id') + '"></li>');
            dlgMsgElem = new Y.ChatDialogMessageView({
                model : msgObj,
                el : $('#dlgelem_' + msgObj.get('id'))
            });
            dlgMsgElem.show();
        },
        prependShowMoreLine : function() {
            var that = this, showMoreElem = this.$el.find('.showmore');
            if(this.model.get('hasMore')) {
                showMoreElem.show();
                showMoreElem.off();
                showMoreElem.click(function(e) {
                    that.loadAndShowOldMessages();
                    return false;
                });
            } else {
                showMoreElem.hide();
            }
        },
        loadAndShowOldMessages : function() {
            var that = this;
            this.dialogManager.loadOldMessages(this.dialogId, function(addedMessagesNum) {
                var msgBlock = that.$el.find('ul'), dlgMessages = that.model.get('messages'), i,
                    lowerBound = that.getPageLowerBound();
                if(addedMessagesNum) {
                    for(i = dlgMessages.length - addedMessagesNum; i < dlgMessages.length; i += 1) {
                        that.prependDialogMessage(msgBlock, dlgMessages[i]);
                    }
                } else {
                    console.warn('No new messages uploaded for ' + that.dialogId);
                }
                that.prependShowMoreLine();
                that.reboundFromPageBottom(lowerBound);
            });
        },
        scrollToSendForm : function() {
            var elemsFound = this.$el.find('.write-message-block');
            if(elemsFound.length > 0) {
                elemsFound[0].scrollIntoView(false);
            }
            elemsFound = this.$el.find('#chat_message_ta');
            if(elemsFound.length > 0) {
                elemsFound[0].focus();
            }
        },
        getPageLowerBound : function() {
            return $(document).height() - $(window).scrollTop();
        },
        reboundFromPageBottom : function(lowerBound) {
            var scrollPt = $(document).height() - lowerBound;
            window.scroll(0, scrollPt);
        }
    });

    ChatDialogMessageView = Backbone.View.extend({
        messageId : '',
        template : msgTemplate,

        initialize : function() {
            this.el = this.options.el;
            this.$el = $(this.el);
            this.messageId = this.model.id;
        },
        show : function() {
            this.render();
        },
        render : function() {
            var msgFullDate = this.model.get('date'),
                msgDate = Y.utils.makeDateString(msgFullDate),
                msgTime = Y.utils.makeHourMinString(msgFullDate),
                fullName = this.model.get('author').get('fullName') + " - " +
                    this.model.get('author').get('companyName'),
                msgText = Y.utils.markLinksForHtml(this.model.get('text')),
                msgItemData = {
                    company_url : '/' + this.model.get('author').get('companyRekId') + '/profile/',
                    employee_url : '/' + this.model.get('author').get('companyRekId') + '/profile/',
                    logo_url : this.model.get('author').get('avatarCommentUrl'),
                    bname : this.model.get('author').get('companyName'),
                    fullname : fullName,
                    fullnamecut : Y.utils.cutLongString(fullName, 50),
                    messagetext : msgText,
                    msgdate : msgDate,
                    msgtime : msgTime
                };
            this.$el.append(this.template(msgItemData));
        }
    });

    Y.ChatDialogView = ChatDialogView;
    Y.ChatDialogMessageView = ChatDialogMessageView;
}
