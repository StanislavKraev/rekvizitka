function x(Y) {
    "use strict";

    var RecommendationsApplicationView, locales = Y.Locales['recommendations_application'];

    RecommendationsApplicationView = Y.GeneralPortlet.extend({

        basicLayoutTemplate:null,
        contractorsView:null,
        docView:null,
        initialized:false,
        photosView:null,
        profileMainView:null,
        recommendationsList:null,
        recommendationsTabs:null,
        tabsCollection:null,
        values:null,
        currentRekId : null,
        own : false,
        ownCompanyRekId : null,

        pages:{
            verification:{
                viewModule:Y.utils.latestVersionName('tab_verification'),
                viewClass:'TabVerification'
            },
            our_proposers:{
                viewModule:Y.utils.latestVersionName('tab_our_proposers'),
                viewClass:'TabOurProposers'
            },
            we_recommend:{
                viewModule:Y.utils.latestVersionName('tab_we_recommend'),
                viewClass:'TabWeRecommend'
            },
            invites:{
                viewModule:Y.utils.latestVersionName('tab_invites'),
                viewClass:'TabInvites'
            }
        },

        portletDataProperty : 'Recommendations_init',
        portletDataLoadURL : '/recommendations/data/',

        initialize:function () {
            this.ownCompanyRekId = this.options.companyRekId;
            this.initRoutes();
        },

        /* overrides from GeneralPortlet */

        getLoadPortletDataURL : function() {
            var rekId = this.activateOptions.rek_id || this.ownCompanyRekId;
            return this.portletDataLoadURL + rekId + '/';
        },

        ifSameData : function() {
            var newRekId = this.activateOptions.rek_id || this.ownCompanyRekId;
            return Y[this.portletDataProperty].rek_id === newRekId;
        },

        childLoadPortletDataSuccess : function() {
            Y[this.portletDataProperty] = this.ajaxResponse.data;
        },

        childLoadPortletDataError : function() {
            Y.Informer.show("Ошибка загрузки рекомендаций: " + this.ajaxError.errorThrown, 30);
        },

        childProcessPortletData : function() {
            var newRekId = this.activateOptions.rek_id || this.ownCompanyRekId;
            this.activateOptions.rerender = (this.currentRekId !== newRekId);
            this.currentRekId = newRekId;
            this.appSettings = this.serverToView(Y[this.portletDataProperty]);
            if(this.appSettings.own) {
                this.ownCompanyRekId = this.appSettings.rek_id;
            }
        },

        childInitializePortlet : function() {
            this.pageToActivate = 'our_proposers';
            this.initRecommendationsList();

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
            if(this.instanceAppended) {
                this.pages[this.pageToActivate].instance.setData({
                        el : this.$el.find('#' + this.pageToActivate),
                        tabContent : this.appSettings
                    });
            } else {
                this.pages[this.pageToActivate].instance = new Y[this.pages[this.pageToActivate].viewClass]({
                    el : this.$el.find('#' + this.pageToActivate),
                    tabContent : this.appSettings
                });
            }
        },

        childUpdateSidebar : function() {
            var sideBarData = {
                'rek_id':this.appSettings.rek_id,
                'avatar':this.appSettings.company_logo,
                'own':this.appSettings.own,
                'authorized':this.appSettings.authorized,
                'sidebarID' : this.options.portal.sidebarID,
                'employee_id':this.appSettings.employee_id,
                'verified' : this.appSettings.verified,
                'nonviewed' : Y[this.portletDataProperty].common_data.unviewed_contractors,
                'we_are_partners' : this.appSettings.we_are_partners
            };
            this.options.mainSidebar.setMode('some_company', sideBarData);
        },

        childOpenPageTab : function() {
            this.recommendationsTabs.openTabById(this.pageToActivate);
        },

        /* overrides end */

        initRoutes:function () {
        },

        initBasicLayout:function () {
            var tab, CCH, data = {}, thisView = this, i, tabdata;

            $.extend(data, {
                brandName:this.appSettings.brandName,
                categoryText:this.appSettings.categoryText,
                rekid:this.currentRekId,
                verified:this.appSettings.verified,
                own:this.appSettings.own,
                authorized : this.appSettings.authorized,
                my_rec_request_status : this.appSettings.my_rec_request_status,
                their_rec_request_status : this.appSettings.their_rec_request_status,
                they_verified : this.appSettings.they_verified
            });

            // todo: currentCompanyHeader doesn't need all information from object "data"
            CCH = new Y.CurrentCompanyHeader({'data':data});

            thisView.$el.append(CCH.render().el);

            this.recommendationsTabs = new Y.TabView({
                el:$('#tabs')
            });

            this.recommendationsTabs.bind('tabChanged', this.onMainTabChanged, this);

            for (i in this.tabsCollection) {
                if (this.tabsCollection.hasOwnProperty(i)) {
                    tab = this.tabsCollection[i];
                    tabdata = {
                        tabIdName : tab.id,
                        tabName :tab.title,
                        tabFullName : tab.title,
                        tabUrl : tab.href
                    };
                    this.recommendationsTabs.addTab(tabdata);
                }
            }
        },

        onMainTabChanged:function (tabId) {
            var url, i, tab;
            for (i in this.tabsCollection) {
                if (this.tabsCollection.hasOwnProperty(i) && this.tabsCollection[i].id === tabId) {
                    tab = this.tabsCollection[i];
                    url = tab.routerUrl;
                    Y.ApplicationRouter.navigate(url, { trigger:true });
                    break;
                }
            }
        },

        serverToView : function(serverData) {
            var viewData = {
                'categoryText' : serverData.categoryText,
                'brandName' : serverData.brandName,
                'rek_id' : serverData.rek_id,
                'own' : serverData.own,
                'sentNotAcceptedList' : serverData.sent_not_accepted_list || [],
                'sentAcceptedList' : serverData.sent_accepted_list || [],
                'receivedAccepted' : serverData.received_accepted || [],
                'receivedNotAccepted' : serverData.received_not_accepted || [],
                'maxRequestCountReached' : serverData.max_req_count_reached || false,
                'sentList' : serverData.sent_invites,
                'sentRegisteredList' : serverData.sent_registered_invites,
                'verifyRecNumber' : serverData.verify_rec_number,
                'authorized' : serverData.authorized,
                'company_logo' : serverData.company_logo,
                'employee_id' : serverData.employee_id,
                'verified' : serverData.common_data.verified,
                'nonviewed' : serverData.common_data.unviewed_contractors,
                'my_rec_request_status' : serverData.common_data.my_rec_request_status,
                'their_rec_request_status' : serverData.common_data.their_rec_request_status,
                'we_are_partners' : serverData.common_data.we_are_contractors || 'no',
                'they_verified' : serverData.common_data.they_verified || false
            };
            if (serverData.bill) {
                viewData.bill = {
                    'id' : serverData.bill.id,
                        'service_title' : serverData.bill.service_title,
                        'price' : serverData.bill.price,
                        'status' : serverData.bill.status,
                        'issued' : serverData.bill.issued,
                        'number' : serverData.bill.number
                };
            }
            return viewData;
        },

        initRecommendationsList:function () {
            this.recommendationsList = {
                companyRekId : this.appSettings.rek_id
            };

            this.tabsCollection = [];
            if (this.appSettings.own && !this.options.verified) {
                this.tabsCollection.push({
                    id : 'verification',
                    href : '/verification/',
                    routerUrl:Y.ApplicationRouter.updateRoute('verification/'),
                    title:'Верификация' // todo: localize
                });
            }

            this.tabsCollection.push({
                id : 'our_proposers',
                href:'/' + this.appSettings.rek_id + '/our_proposers/',
                routerUrl:Y.ApplicationRouter.updateRoute(this.appSettings.rek_id + '/our_proposers/'),
                title:'Нас рекомендуют'
            });

            this.tabsCollection.push({
                id : 'we_recommend',
                href:'/' + this.appSettings.rek_id + '/we_recommend/',
                routerUrl:Y.ApplicationRouter.updateRoute(this.appSettings.rek_id + '/we_recommend/'),
                title:'Мы рекомендуем'
            });

            if (this.options.verified && this.appSettings.own) {
                this.tabsCollection.push({
                    id : 'invites',
                    href:'/invites/',
                    routerUrl:Y.ApplicationRouter.updateRoute('invites/'),
                    title:'Приглашения'
                });
            }
        }
    });

    Y.RecommendationsApplication = RecommendationsApplicationView;
}
