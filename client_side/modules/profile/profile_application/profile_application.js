function x(Y) {
    "use strict";

    var ProfileAppView;

    ProfileAppView = Y.GeneralPortlet.extend({
        appSettings:null,

        basicLayoutTemplate:null,

        profileMainView:null,
        contractorsView:null,
        photosView:null,
        docView:null,
        initialized:false,
        currentRekId:null,

        settingsList:null,

        active:false,
        tabView:null,

        delayedRender : null,

        tabsCollection:null,
        locales :Y.Locales['profile_application'],

        pages:{
            /*
             main : {
             viewModule : Y.utils.latestVersionName('profile_main_view'),
             viewClass : 'ProfileMainView'
             },
             */
            profile:{
                viewModule:Y.utils.latestVersionName('profile_about_view'),
                viewClass:'ProfileAboutView'
            },
            contacts:{
                viewModule:Y.utils.latestVersionName('profile_contacts_view'),
                viewClass:'ProfileContactsView'
            }
            /*,
             employees : {
             viewModule : Y.utils.latestVersionName('profile_employees_view'),
             viewClass : 'ProfileEmployeesView'
             },
             contractors : {
             viewModule : Y.utils.latestVersionName('profile_contractors_view'),
             viewClass : 'ProfileContractorsView'
             },
             docs : {
             viewModule : Y.utils.latestVersionName('profile_doc_view'),
             viewClass : 'ProfileDocView'
             },
             photos : {
             viewModule : Y.utils.latestVersionName('profile_photos_view'),
             viewClass : 'ProfilePhotosView'
             }
             */
        },

        portletDataProperty : 'ProfileAppSettings_init',
        portletDataLoadURL : '/profile/i/',

        initialize:function () {
            this.delayedRender = [];
            this.activateOptions = {};
            this.initRoutes();
        },

        /* overrides from GeneralPortlet */

        getLoadPortletDataURL : function() {
            return this.portletDataLoadURL + this.activateOptions.rek_id;
        },

        childLoadPortletDataSuccess : function() {
            Y[this.portletDataProperty] = this.ajaxResponse.data;
        },

        childLoadPortletDataError : function() {
            Y.Informer.show("Ошибка загрузки профиля: " + this.ajaxError.errorThrown, 30);
        },

        ifSameData : function() {
            return Y[this.portletDataProperty].rek_id === this.activateOptions.rek_id;
        },

        childProcessPortletData : function() {
            var emptyInfo;
            this.appSettings = Y[this.portletDataProperty];
            this.activateOptions.rerender = (this.currentRekId !== this.activateOptions.rek_id);
            this.currentRekId = this.activateOptions.rek_id;
            emptyInfo = Y.testServerData.findNonfilledProps(this.appSettings.profile.information);
            if (emptyInfo.length > 0) {
                Y.utils.fillEmptyProps(this.appSettings.profile.information, emptyInfo);
            }
        },

        childInitializePortlet : function() {
            this.pageToActivate = 'profile';

            this.initSettingsList();

            if(this.activateOptions.page &&
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
                this.$el.empty();
                this.preparedUi = null;
                this.tabView = null;
                this.initialized = false;  // clean this.pages instances?
            }
            return true;
        },

        childUpdatePageInstance : function() {
            if(this.instanceAppended) {
                this.pages[this.pageToActivate].instance.setData({
                    el : this.$el.find('#' + this.pageToActivate),
                    thisProfileApplication : this
                });
            } else {
                this.pages[this.pageToActivate].instance = new Y[this.pages[this.pageToActivate].viewClass]({
                    el : this.$el.find('#' + this.pageToActivate),
                    thisProfileApplication : this
                });
            }
        },

        childUpdateSidebar : function() {
            var sideBarData = {
                'rek_id' : this.appSettings.rek_id,
                'avatar' : this.appSettings.company_logo,
                'own' : this.appSettings.own_company,
                'sidebarID' : this.options.portal.sidebarID,
                'authorized' : this.appSettings.authorized,
                'employee_id' : this.appSettings.employee_id,
                'verified' : this.appSettings.common_data.verified,
                'we_are_partners' : this.appSettings.common_data.we_are_contractors,
                'nonviewed' : this.appSettings.common_data.unviewed_contractors
            };
            this.options.mainSidebar.setMode('some_company', sideBarData);
        },

        childOpenPageTab : function() {
            this.tabView.openTabById(this.pageToActivate);
        },

        /* overrides end */

        initRoutes:function () {
            var portal = this.options.portal;

            Y.ApplicationRouter.route(/^([0-9A-Z]+)\/contacts\/$/, 'profile_contacts', function (rek_id) {
                portal.activatePortlet('profile_about', {rek_id:rek_id, page:'contacts'});
            });
        },

        initBasicLayout:function () {
            var tabId, tab, CCH, data = {}, thisView = this, tabdata;

            $.extend(data, {
                brandName:this.appSettings.profile.information.brandName,
                categoryText:this.appSettings.profile.information.categoryText,
                rekid:this.appSettings.rek_id,
                verified:this.appSettings.common_data.verified,
                own:this.appSettings.own_company,
                portal:this.options.portal,
                authorized : this.appSettings.authorized,
                my_rec_request_status : this.appSettings.common_data.my_rec_request_status,
                their_rec_request_status : this.appSettings.common_data.their_rec_request_status,
                they_verified : this.appSettings.common_data.they_verified
            });

            CCH = new Y.CurrentCompanyHeader({'data':data});

            thisView.$el.append(CCH.render().el);

            this.tabView = new Y.TabView({
                el:$('#tabs')
            });

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

        onMainTabChanged:function (tabId) {
            var url = this.tabsCollection[tabId].routerUrl;
            Y.ApplicationRouter.navigate(url, {trigger:true});
        },

        initSettingsList : function () {
            this.settingsList = {
                companyRekId:this.options.companyRekId
            };

            this.tabsCollection = {
                profile:{
                    href:'/' + this.currentRekId + '/profile/',
                    routerUrl:Y.ApplicationRouter.updateRoute(this.currentRekId + '/profile/'),
                    title:this.locales.about
                },
                contacts:{
                    href:'/' + this.currentRekId + '/contacts/',
                    routerUrl:Y.ApplicationRouter.updateRoute(this.currentRekId + '/contacts/'),
                    title:this.locales.contacts
                }
            };
        },

        doAjax:function (ajaxPath, data, successCallBack) {
            var thisView = this;

            $.ajax(ajaxPath, {
                success:successCallBack,
                error:function () {
                    Y.Informer.show(thisView.locales.errorCantSaveChanges, 10);
                },
                type:'POST',
                data:data,
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        moduleProcessContacts:function (data, childView) {
            var thisView = this, officeData;

            function onSendAjaxSuccess(data) {
                var i;

                if (data.success) {
                    thisView.appSettings.contacts.phone = data.data.main_phone;
                    thisView.appSettings.contacts.email = data.data.main_email;
                    thisView.appSettings.contacts.site = data.data.main_site;

                    thisView.appSettings.contacts.offices = [];

                    for (i = 0; i < data.data.offices.length; i += 1) {
                        officeData = {
                            'city':data.data.offices[i].city,
                            'information':data.data.offices[i].information,
                            'imgID':data.data.offices[i].imgID,
                            'img_src':data.data.offices[i].img_src,
                            'img_width':data.data.offices[i].img_width,
                            'img_height':data.data.offices[i].img_height};

                        thisView.appSettings.contacts.offices.push(officeData);
                    }

                    childView.officeViewList = [];

                    childView.setData({
                        thisProfileApplication:thisView
                    });
                } else {
                    Y.Informer.show(thisView.locales.errorCantSaveContacts, 10);
                }
            }

            this.doAjax('/profile/edit/', {act:'cnt', data:data}, onSendAjaxSuccess);
        },

        moduleProcessAbout:function (data, childView) {
            var thisView = this;

            function onSendAjaxSuccess(data) {
                var serverData, i;

                if (data.success && data.data) {
                    serverData = data.data;

                    $('#content h1').text(serverData.brandName);
                    $('.logged-in .name-title h4').text(serverData.brandName);

                    Y.ProfileAppSettings_init = null;

                    thisView.appSettings.profile.descr = serverData.descr;
                    thisView.appSettings.staffSize = serverData.staffSize;

                    for (i in thisView.appSettings.profile.information) {
                        if (thisView.appSettings.profile.information.hasOwnProperty(i)) {
                            thisView.appSettings.profile.information[i] = serverData[i];
                        }
                    }

                    for (i in thisView.appSettings.profile.essential_elements) {
                        if (thisView.appSettings.profile.essential_elements.hasOwnProperty(i)) {
                            thisView.appSettings.profile.essential_elements[i] = serverData.bank_account[i];
                        }
                    }

                    childView.setData({
                        thisProfileApplication:thisView
                    });

                    $('body')[0].scrollIntoView(true);
                } else {
                    Y.Informer.show(thisView.locales.errorCantSaveAbout, 20);
                }
            }

            this.doAjax('/profile/edit/', {act:'gi', data:data}, onSendAjaxSuccess);
        }

    });

    Y.ProfileApplication = ProfileAppView;
}
