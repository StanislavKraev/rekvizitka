function x(Y) {
    "use strict";

    var Settings, appResources = Y.Locales['settings'];

    Settings = Y.GeneralPortlet.extend({

        appSettings:null,

        basicLayoutTemplate:null,

        profileMainView:null,
        contractorsView:null,
        photosView:null,
        docView:null,
        initialized:false,

        settingsList:null,

        active:false,
        settingsTabs:null,

        tabsCollection:null,

        activateOptions : null,

        locales : Y.Locales['settings_application'],
        pages : {
            settings : {
                viewModule : Y.utils.latestVersionName('profile_settings_view'),
                viewClass : 'ProfileSettingsView'
            },
            additional_settings : {
                viewModule : Y.utils.latestVersionName('profile_additional_settings_view'),
                viewClass : 'ProfileAdditionalSettingsView'
            },
            change_password : {
                viewModule : Y.utils.latestVersionName('change_password_view'),
                viewClass : 'ChangePasswordView'
            }
        },

        portletDataProperty : 'Settings_init',
        portletDataLoadURL : '/settings/s/',

        initialize : function () {
            this.activateOptions = {};
            this.initRoutes();
        },

        /* overrides from GeneralPortlet */

        getLoadPortletDataURL : function() {
            return this.portletDataLoadURL;
        },

        childLoadPortletDataSuccess : function() {
            Y[this.portletDataProperty] = this.ajaxResponse.data;
        },

        childLoadPortletDataError : function() {
            Y.Informer.show("Ошибка загрузки настроек: " + this.ajaxError.errorThrown, 30);
        },

        childProcessPortletData : function() {
            var emptyInfo;
            this.currentRekId = this.options.companyRekId;
            this.appSettings = Y[this.portletDataProperty];
            emptyInfo = Y.testServerData.findNonfilledProps(this.appSettings);
            if(emptyInfo.length > 0) {
                Y.utils.fillEmptyProps(this.appSettings, emptyInfo);
            }
        },

        childInitializePortlet : function() {
            this.pageToActivate = 'settings';
            this.initSettingsList();

            this.activateOptions = $.extend(this.activateOptions, { rerender : false });

            if (this.activateOptions.page &&
                this.pages.hasOwnProperty(this.activateOptions.page)) {
                this.pageToActivate = this.activateOptions.page;
            }
            return true;
        },

        childPageInstanceActivated : function() {
            this.instanceAppended = this.pages[this.pageToActivate].hasOwnProperty('instance');
            return this.instanceAppended;
        },

        getClassModuleName : function() {
            return this.pages[this.pageToActivate].viewModule;
        },

        childPrepareDrawPortlet : function() {
            if(this.initialized && this.activateOptions.rerender) {
                this.preparedUi = null;
                this.$el.empty();
                this.initialized = false;
            }
            return true;
        },

        childUpdatePageInstance : function() {
            if(!this.instanceAppended) {
                this.pages[this.pageToActivate].instance = new Y[this.pages[this.pageToActivate].viewClass]({
                    el : this.$el.find('#' + this.pageToActivate),
                    tab_content : this.appSettings,
                    containerApplication : this
                });
            }
        },

        childUpdateSidebar : function() {
            var sideBarData = {
                'rek_id' : this.options.portal.options.companyRekId,
                'avatar' : this.options.portal.options.company_logo_url,
                'own' : this.options.portal.options.own_company,
                'authorized' : this.options.portal.options.authorized,
                'verified' : this.options.portal.options.verified,
                'sidebarID' : this.options.portal.sidebarID,
                'nonviewed' : Y[this.portletDataProperty].common_data.unviewed_contractors
            };
            this.options.mainSidebar.setMode('some_company', sideBarData);
        },

        childOpenPageTab : function() {
            this.settingsTabs.openTabById(this.pageToActivate);
        },
        /* overrides end */

        initSettingsList : function () {
            this.settingsList = {
                companyRekId : this.options.companyRekId
            };

            this.tabsCollection = {
                settings : {
                    href : '/settings/',
                    routerUrl : Y.ApplicationRouter.updateRoute('settings/'),
                    title : this.locales.mainSettingsTab
                },
                additional_settings : {
                    href : '/additional-settings/',
                    routerUrl : Y.ApplicationRouter.updateRoute('additional-settings/'),
                    title: this.locales.additionalSettingsTab
                },
                change_password : {
                    href: '/change-password/',
                    routerUrl : Y.ApplicationRouter.updateRoute('change-password/'),
                    title : this.locales.passwordTab
                }
            };
        },

        initRoutes : function () {
            var portal = this.options.portal;

            Y.ApplicationRouter.route(/^additional-settings\/$/, 'additional-settings', function () {
                portal.activatePortlet('portlet_settings', {'page' : 'additional_settings'});
            });

            Y.ApplicationRouter.route(/^change-password\/$/, 'change-password', function() {
                portal.activatePortlet('portlet_settings', { 'page' : 'change_password' });
            });
        },

        initBasicLayout : function () {
            var tabId, tab, CCH, data = {}, thisView = this, portal = this.options.portal, tabdata;

            $.extend(data, {
                brandName : portal.options.brandName,
                categoryText : this.appSettings.categoryText,
                rekid : this.options.companyRekId,
                verified : this.appSettings.common_data.verified,
                own : this.options.portal.options.own_company,
                authorized : this.options.portal.options.authorized,
                my_rec_request_status : this.appSettings.common_data.my_rec_request_status,
                their_rec_request_status : this.appSettings.common_data.their_rec_request_status
            });

            CCH = new Y.CurrentCompanyHeader({'data':data});

            thisView.$el.append(CCH.render().el);

            this.settingsTabs = new Y.TabView({
                el:$('#tabs')
            });

            this.settingsTabs.bind('tabChanged', this.onMainTabChanged, this);

            for(tabId in this.tabsCollection) {
                if(this.tabsCollection.hasOwnProperty(tabId)) {
                    tab = this.tabsCollection[tabId];
                    tabdata = {
                        tabIdName : tabId,
                        tabName : tab.title,
                        tabFullName : tab.title,
                        tabUrl : tab.href
                    };
                    this.settingsTabs.addTab(tabdata);
                }
            }
        },

        onMainTabChanged : function(tabId) {
            var url = this.tabsCollection[tabId].routerUrl;
            Y.ApplicationRouter.navigate(url, { trigger : true });
        },

        saveNewPassword : function(saveData, params, callbackSuccess, callbackError) {
            $.ajax('/profile/change_pwd/', {
                success : function(data) {
                              callbackSuccess(params, data);
                          },
                error : function() {
                              callbackError(params);
                          },
                type : 'POST',
                data : saveData,
                dataType : 'json',
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        }
    });

    Y.ProfileSettings = Settings;
}
