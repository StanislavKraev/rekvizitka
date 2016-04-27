function x(Y) {
    "use strict";

    var ChatApplicationView;

    ChatApplicationView = Y.GeneralPortlet.extend({
        locales : Y.Locales['chat_application'],
        appChat : null,
        initialized : false,
        tabsCollection : null,
        tabOrder : 1,
        pageClasses : {
            dialog_list : {
                viewModule : Y.utils.latestVersionName('chat_dialog_list_view'),
                viewClass : 'ChatDialogListView'
            },
            dialog : {
                viewModule : Y.utils.latestVersionName('chat_dialog_view'),
                viewClass : 'ChatDialogView'
            }
        },
        chatTabs : null,
        $chatContent : null,
        preparedUi : null,
        newDialogOpenId : null,
        listPage : 1,
        currentTabId : 'dialog_list',

        dialogManager : Y.ChatDialogManager,

        portletDataProperty : 'Chat_init',
        portletDataLoadURL : '/chat/',

        initialize : function() {
            this.initTabs();
            this.dialogManager.on("newMessage", this.onNewMessage, this);
        },

        initTabs : function() {
            this.tabsCollection = {
                dialog_list : {
                    href : '/chat/',
                    routerUrl : '',
                    title : this.locales.my_dialogs,
                    instance : null,
                    order : 0
                }
            };
        },

        /* overrides from GeneralPortlet */

        hasDataManager : function() {
            return true;
        },

        childInitDataThroughManager : function(callback) {
            var dialogId, that = this;
            if(this.activateOptions) {
                if (this.activateOptions.page === 'dialog') {
                    this.dialogManager.initFromDialog(callback, this.activateOptions.dialogId);
                } else if(this.activateOptions.corrId) {
                    dialogId = null;
                    $.each(this.dialogManager.dialogs, function(id, iterDialog) {
                        if (iterDialog.get('visavis').get('id') === that.activateOptions.corrId) {
                            dialogId = iterDialog.get('id');
                            return false;
                        }
                    });
                    if (dialogId && this.dialogManager.dialogs.hasOwnProperty(dialogId)) {
                        this.activateOptions.page = 'dialog';
                        this.activateOptions.dialogId = dialogId;
                        Y.ApplicationRouter.navigate('/chat/dialog/' + dialogId + '/', { trigger : false, replace : true });
                        $.extend(this.activateOptions, {
                            page : 'dialog',
                            dialogId : dialogId
                        });
                        this.dialogManager.initFromDialog(callback, dialogId);
                    } else {
                        this.dialogManager.createDialog(that.activateOptions.corrId, function (dialog) {
                            if(!dialog) {
                                Y.ApplicationRouter.navigate('/chat/', { trigger : true });
                                Y.Informer.show("Ошибка открытия диалога!", 10);
                                callback();
                            } else {
                                if(!Y.hasOwnProperty(that.portletDataProperty)) {
                                    Y[that.portletDataProperty] = {};
                                }
                                $.extend(Y[that.portletDataProperty], {
                                    company_logo : that.dialogManager.company_logo,
                                    brandName : that.dialogManager.brandName,
                                    emplid : that.dialogManager.emplid,
                                    rekid : that.dialogManager.rekid,
                                    employeeName : that.dialogManager.employeeName
                                });
                                Y.ApplicationRouter.navigate('/chat/dialog/' + dialog.get('id') + '/', { trigger : false, replace : true });
                                $.extend(that.activateOptions, {
                                    page : 'dialog',
                                    dialogId : dialog.get('id')
                                });
                                that.dialogManager.initFromDialog(callback, dialog.get('id'));
                            }
                        });
                    }
                } else {
                    this.dialogManager.initFromDialogList(callback);
                }
            } else {
                this.dialogManager.initFromDialogList(callback);
            }
        },

        childInitializePortlet : function() {
            this.initChatList();
            this.pageToActivate = 'dialog_list';
            this.openNewTab = false;

            if(this.activateOptions && this.activateOptions.page === 'dialog') {
                if(!this.tabsCollection.hasOwnProperty(this.activateOptions.dialogId)) {
                    this.openNewTab = true;
                }
                this.pageToActivate = this.activateOptions.dialogId;
            }
            return true;
        },

        childPageInstanceActivated : function() {
            this.instanceAppended = (this.tabsCollection.hasOwnProperty(this.pageToActivate) &&
                                        this.tabsCollection[this.pageToActivate].hasOwnProperty('instance') &&
                                        this.tabsCollection[this.pageToActivate].instance !== null);
            return this.instanceAppended;
        },

        getClassModuleName : function() {
            var pageClass = (this.pageToActivate === 'dialog_list' ? 'dialog_list' : 'dialog');
            return this.pageClasses[pageClass].viewModule;
        },

        childPrepareDrawPortlet : function() {
            return true;
        },

        childUpdatePageInstance : function() {
            var correspondent, tabElement, pageId, viewClass;

            if(this.openNewTab) {
                correspondent = this.dialogManager.getCorrFromDialogId(this.pageToActivate);
                if (!correspondent) {
                    console.error('Failed to open tab for dialog ' + this.pageToActivate + ': correspondent party was not found/loaded');
                    this.pageToActivate = 'dialog_list';
                } else {
                    if(!this.tabsCollection.hasOwnProperty(this.pageToActivate)) {
                        this.tabsCollection[this.pageToActivate] = {
                            href : '/chat/dialog/' + this.pageToActivate + '/',
                            routerUrl : '',
                            title : correspondent.get('companyName'),
                            order : this.tabOrder,
                            instance : null
                        };
                        this.tabOrder += 1;
                        this.newDialogOpenId = this.pageToActivate;
                        this.instanceAppended = false;
                        this.appendDialogTabView();
                    }
                }
            }

            tabElement = this.tabsCollection[this.pageToActivate];

            if(!this.instanceAppended) {
                pageId = (this.pageToActivate === 'dialog_list' ? 'dialog_list' : 'dialog');
                viewClass = this.pageClasses[pageId].viewClass;
                tabElement.instance = new Y[viewClass]({
                    dialogId : this.pageToActivate,
                    container : this.chatTabs,
                    el : this.$el.find('#' + this.pageToActivate)
                });
            } else {
                tabElement.instance.setData({
                    container : this.chatTabs,
                    dialogId : this.pageToActivate,
                    el : this.$el.find('#' + this.pageToActivate)
                });
            }
        },

        childUpdateSidebar : function() {
            var sideBarData = {
                'rek_id' : Y[this.portletDataProperty].rekid,
                'avatar' : Y[this.portletDataProperty].company_logo,
                'own' : true,
                'authorized' : true,
                'sidebarID' : this.options.portal.sidebarID,
                'employee_id' : Y[this.portletDataProperty].emplid,
                'nonviewed' : 0
            };
            this.options.mainSidebar.setMode('some_company', sideBarData);
        },

        childOpenPageTab : function() {
            this.tabsCollection[this.pageToActivate].routerUrl =
                  Y.ApplicationRouter.updateRoute(this.tabsCollection[this.pageToActivate].href.substring(1));
            this.tabsCollection[this.pageToActivate].unreadMsgs = 0;

            this.currentTabId = this.pageToActivate;
            this.chatTabs.openTabById(this.pageToActivate);
            this.chatTabs.resetUnreadState(this.pageToActivate);
            this.tabsCollection[this.pageToActivate].instance.afterShow();
        },

        /* overrides end */

        initChatList : function() {
            var i;
            for(i in this.tabsCollection) {
                if(this.tabsCollection.hasOwnProperty(i)) {
                    this.tabsCollection[i].routerUrl = Y.ApplicationRouter.updateRoute(this.tabsCollection[i].href);
                }
            }
        },

        initBasicLayout : function() {
            var emplData = {}, chatHeader;
            $.extend(emplData, {
                brandName : this.dialogManager.brandName,
                employeeName : this.dialogManager.employeeName
            });

            chatHeader = new Y.CurrentEmployeeHeader({ 'data' : emplData });
            this.$el.append(chatHeader.render().el);
            this.initTabView();
        },

        initTabView : function() {
            var i, cttab, tabdata;
            this.chatTabs = new Y.TabView({ el : '#tabs', type : 'dynamic' });
            this.chatTabs.bind('tabChanged', this.onChatTabChanged, this);
            this.chatTabs.bind('newTabOpen', this.onChatNewDialogTab, this);
            this.chatTabs.bind('closeDynamicTab', this.onChatCloseDialogTab, this);
            this.chatTabs.bind('markDialogRead', this.onMarkDialogRead, this);

            tabdata = {
                tabIdName : 'dialog_list',
                tabName : Y.utils.cutLongString(this.tabsCollection['dialog_list'].title, 16),
                tabFullName : this.tabsCollection['dialog_list'].title,
                tabUrl : this.tabsCollection['dialog_list'].href
            };
            this.chatTabs.addTab(tabdata);

            for(i in this.tabsCollection) {
                if(this.tabsCollection.hasOwnProperty(i) && i !== 'dialog_list') {
                    cttab = this.tabsCollection[i];
                    tabdata = {
                        tabIdName : i,
                        tabName : Y.utils.cutLongString(cttab.title, 16),
                        tabFullName : cttab.title,
                        tabUrl : cttab.href
                    };
                    this.chatTabs.addDynamicTab(tabdata);
                }
            }
            this.newDialogOpenId = null;
        },

        onChatTabChanged : function(tabId) {
            var routeUrl = this.tabsCollection[tabId].routerUrl;
            if(tabId === 'dialog_list') {
                routeUrl += '?p=' + this.listPage;
            } else if(this.currentTabId === 'dialog_list') {
                this.listPage = this.tabsCollection['dialog_list'].instance.chatCurrentPage;
            }
            Y.ApplicationRouter.navigate(routeUrl, { trigger : true });
        },

        onChatNewDialogTab : function(data) {
            if(this.currentTabId === 'dialog_list') {
                this.listPage = this.tabsCollection['dialog_list'].instance.chatCurrentPage;
            }
            Y.ApplicationRouter.navigate('/chat/dialog/' + data.dialogId + '/', { trigger : true });
            if(data.callback) {
                data.callback();
            }
        },

        onChatCloseDialogTab : function(tabId) {
            var i, delOrder, activateId, routeUrl;
            if(this.tabsCollection.hasOwnProperty(tabId)) {
                delOrder = this.tabsCollection[tabId].order;
                activateId = this.chatTabs.removeDynamicTab(tabId);
                delete this.tabsCollection[tabId];
                for(i in this.tabsCollection) {
                    if(this.tabsCollection.hasOwnProperty(i)) {
                        if(this.tabsCollection[i].order > delOrder) {
                            this.tabsCollection[i].order -= 1;
                        }
                    }
                }
                this.tabOrder -= 1;
                if(activateId) {
                    routeUrl = this.tabsCollection[activateId].routerUrl;
                    if(activateId === 'dialog_list') {
                        routeUrl += '?p=' + this.listPage;
                    }
                    Y.ApplicationRouter.navigate(routeUrl, { trigger : true });
                }
            }
            /* this.tabOrder -= 1;
            if(activateId) {
                Y.ApplicationRouter.navigate(this.tabsCollection[activateId].routerUrl, { trigger : true });
            }*/
        },

        onNewMessage : function(msgData) {
            var dlgId = msgData.dialog.get('id'), msgId = msgData.message.get('id');

            if (this.tabsCollection.hasOwnProperty(dlgId) &&
                    !this.chatTabs.isActiveTab(dlgId) &&
                    this.chatTabs.getTabContentById(dlgId).find('#dlgelem_' + msgId).length < 1) {
                this.tabsCollection[dlgId].unreadMsgs += 1;
                this.chatTabs.highlightTab(dlgId, this.tabsCollection[dlgId].unreadMsgs);
            }
        },

        onMarkDialogRead : function(data) {
            var isViewed = false;
            if(this.chatTabs.currentPage > 0 &&
                this.chatTabs.tabs[this.chatTabs.currentPage][0] === data.dialogId) {
                this.dialogManager.dialogs[data.dialogId].set('isViewed', true);
                this.dialogManager.markDialogAsRead(data.dialogId);
                this.dialogManager.trigger('markDialogRead', { dialogId : data.dialogId });
                isViewed = true;
            }
            if(data.callback) {
                data.callback(isViewed);
            }
        },

        appendDialogTabView : function() {
            var tabdata;
            if(this.newDialogOpenId) {
                tabdata = {
                    tabFullName : this.tabsCollection[this.newDialogOpenId].title,
                    tabName : Y.utils.cutLongString(this.tabsCollection[this.newDialogOpenId].title, 16),
                    tabIdName : this.newDialogOpenId,
                    tabUrl : this.tabsCollection[this.newDialogOpenId].href
                };
                this.chatTabs.addDynamicTab(tabdata);
                this.newDialogOpenId = null;
            }
        },

        createOrOpenDialog : function(companionId) {
            var existDlg = this.dialogManager.getDialogIdWithCorr(companionId), that = this;

            function createDialogTail(dialogId) {
                if(dialogId) {
                    Y.ApplicationRouter.navigate('/chat/dialog/' + dialogId + '/', { trigger : true, replace : true });
                } else {
                    Y.ApplicationRouter.navigate('/chat/', { trigger : true });
                    Y.Informer.show("Ошибка открытия диалога", 10);
                }
            }

            if(existDlg) {
                this.onChatTabChanged(existDlg);
                return;
            }
            this.dialogManager.createDialog(companionId, createDialogTail);
        },

        getCorrespondentFromTabId : function(tabId) {
            var corrRef = null, dialog, dialogId, corrPretendent, corrMap;
            for (dialogId in this.dialogManager.dialogs) {
                if (this.dialogManager.dialogs.hasOwnProperty(dialogId)) {
                    dialog = this.dialogManager.dialogs[dialogId];
                    if (dialog.get('id') === tabId) {
                        corrMap = dialog.get('correspts');
                        for(corrPretendent in corrMap) {
                            if(corrMap.hasOwnProperty(corrPretendent) &&
                                corrPretendent !== this.dialogManager.emplid) {
                                corrRef = corrMap[corrPretendent];
                                break;
                            }
                        }
                        if(corrRef) {
                            break;
                        }
                    }
                }
            }
            return corrRef;
        }
    });

    Y.ChatApplicationView = ChatApplicationView;
}
