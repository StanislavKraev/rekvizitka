function x(Y) {
    "use strict";

    var SidebarView,
        MessagingAppView,
        appResources = Y.Locales['messaging_application'];

    MessagingAppView = Backbone.View.extend({
        tabView : null,
        sidebar : null,
        appSettings : null,
        letterTabView : null,
        contactsTabView : null,
        basicLayoutTemplate : Y.TemplateStore.load('messaging_application_basic_layout'),
        initialized : false,
        active : false,
        preparedUi : null,
        tabsCollection : {
            letters_page : {
                routerUrl : "",
                title : appResources['letters_tab_name']
            },
            contacts_page : {
                routerUrl : "contacts/",
                title : appResources['contacts_tab_name']
            },
            settings_page : {
                routerUrl : "settings/",
                title : appResources['settings_tab_name']
            }
        },

        initialize : function() {
            this.initSettings();
            this.initRoutes();
        },

        activate : function(options) {
            if (!this.initialized) {
                this.initBasicLayout();
                this.initialized = true;
            } else {
                if (this.preparedUi) {
                    this.$el.append(this.preparedUi);
                    this.preparedUi = null;
                }
            }

            if (options && options.page) {
                if (options.page === 'contacts') {
                    this.openContactsView();
                } else if (options.page === 'settings') {
                    this.openSettingsView();
                } else {
                    this.openLettersView();
                }
            } else {
                this.openLettersView();
            }
            this.active = true;
        },

        deactivate : function() {
            this.preparedUi = this.$el.children().detach();
            this.active = false;
        },

        initRoutes : function() {
            var app = this;
            Y.ApplicationRouter.route(this.appSettings.hashNavBaseUrl + 'letters/', 'letters_list', function () {
                app.activate();
            });
            Y.ApplicationRouter.route(this.appSettings.hashNavBaseUrl + 'contacts/', 'contacts_list', function () {
                app.activate({page : 'contacts'});
            });
            Y.ApplicationRouter.route(this.appSettings.hashNavBaseUrl + 'settings/', 'settings_tab', function () {
                app.activate({page : 'settings'});
            });
        },

        initBasicLayout : function() {
            var tabId, tab, tabdata;
            this.$el.append(this.basicLayoutTemplate());

            this.sidebar = new SidebarView({el : $("#mail_sidebar")});

            this.tabView = new Y.TabView({el : $('#tabs')});
            this.tabView.bind('tabChanged', this.onMainTabChanged, this);

            for (tabId in this.tabsCollection) {
                if (this.tabsCollection.hasOwnProperty(tabId)) {
                    tab = this.tabsCollection[tabId];
                    tabdata = {
                        tabIdName : tabId,
                        tabName :Y.utils.cutLongString(tab.title, 16),
                        tabFullName : tab.title,
                        tabUrl : tab.href
                    };
                    this.tabView.addTab(tabdata);
                }
            }
        },

        initSettings : function() {
            if (Y.MessagingAppSettings_init) {
                this.appSettings = Y.MessagingAppSettings_init;
            } else {
                Y.log('Messaging settings are not loaded.', 'error', 'MessagingApplication');
            }
        },

        onMainTabChanged : function(tabId) {
            var url = this.appSettings.hashNavBaseUrl + this.tabsCollection[tabId].routerUrl;
            Y.ApplicationRouter.navigate(url, {trigger : true});
        },

        openLettersView : function() {
            var appView = this;
            if (!appView.letterTabView) {
                Y.use(Y.utils.latestVersionName('message_view'),
                      Y.utils.latestVersionName('mail_sidebar'), function(Y) {
                    var sidebarView = new Y.MailSidebarView({
                        defaultMailFolder : appView.appSettings.defaultMailFolder,
                        folderList : appView.appSettings.folderList,
                        sid : "letters_page"
                    });
                    appView.letterTabView = new Y.MessageView({rootDomElement: "#letters_page",
                        fetchUrl : appView.appSettings.fetchUrl,
                        messagesOnPage : appView.appSettings.messagesOnPage,
                        defaultMailFolder : appView.appSettings.defaultMailFolder,
                        folderList : appView.appSettings.folderList
                    });
                    appView.sidebar.addView(sidebarView);

                    sidebarView.bind('folderSelected', appView.letterTabView.onMailFolderChange, appView.letterTabView);
                    appView.letterTabView.bind('mailFolderItemsCountChanged', appView.onMailFolderItemsCountChanged, sidebarView);

                    appView.sidebar.switchView("letters_page");
                });
            } else {
                appView.sidebar.switchView("letters_page");
                appView.letterTabView.activate();
            }
            this.tabView.openTabById("letters_page");
        },

        onMailFolderItemsCountChanged : function(folderId, newCount) {
            var sidebarView = this;
            sidebarView.setFolderItemsCount(folderId, newCount);
        },

        openSettingsView : function() {
        },

        openContactsView : function() {
            var appView = this;
            if (!appView.contactsTabView) {
                Y.use(Y.utils.latestVersionName('contacts_view'),
                      Y.utils.latestVersionName('contacts_sidebar'), function(Y) {
                    appView.contactsTabView = new Y.ContactsView({el : $("#contacts_page")});
                    // todo: initialize ContactsSidebarView
                    // todo: connect appView and sidebarView here
                    appView.sidebar.switchView("contacts_page");
                });
            } else {
                appView.sidebar.switchView("contacts_page");
            }
            this.tabView.openTabById("contacts_page");
        }
    });

    SidebarView = Backbone.View.extend({
        views : {},
        switchView : function(viewId) {
            var view, viewObject;
            for (view in this.views) {
                if (this.views.hasOwnProperty(view)) {
                    viewObject = this.views[view];
                    if (viewObject.sid === viewId) {
                        viewObject.show();
                    } else {
                        viewObject.hide();
                    }
                }
            }
        },
        addView : function(sidebarView) {
            var viewId = sidebarView.sid;
            if (!this.views.hasOwnProperty(viewId)) {
                this.views[viewId] = sidebarView;
                this.$el.append(sidebarView.render().el);

                if (this.views.length === 1) {
                    sidebarView.show();
                } else {
                    sidebarView.hide();
                }
            }
        }
    });

    Y.MessagingApplication = MessagingAppView;
}
