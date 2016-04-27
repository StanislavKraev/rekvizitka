function x(Y) {
    "use strict";

    var DepositApplicationView, locales = Y.Locales['deposit_application'];

	DepositApplicationView = Y.GeneralPortlet.extend({

	values : null,

        basicLayoutTemplate : null,

        profileMainView : null,
        contractorsView : null,
        photosView : null,
        docView : null,
        initialized : false,

        depositList : null,

        active : false,
        depositTabs : null,

        tabsCollection : null,

        portletDataProperty : 'Deposit_init',
        portletDataLoadURL : '/deposit/s/',

        pages : {
            deposit : {
                viewModule : Y.utils.latestVersionName('tab_deposit'),
                viewClass : 'TabDeposit'
            },
            topping_up : {
                viewModule : Y.utils.latestVersionName('tab_topping_up'),
                viewClass : 'TabToppingUp'
            },
            payments : {
                viewModule : Y.utils.latestVersionName('tab_payments'),
                viewClass : 'TabPayments'
            }
        },

        initialize : function() {
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
            Y.Informer.show("Ошибка загрузки депозита: " + this.ajaxError.errorThrown, 30);
        },

        childProcessPortletData : function() {
            var emptyProps;
            this.appDeposit = Y[this.portletDataProperty];
            emptyProps = Y.testServerData.findNonfilledProps(this.appDeposit);
            if(emptyProps.length > 0) {
                Y.utils.fillEmptyProps(this.appDeposit, emptyProps);
            }
        },

        childInitializePortlet : function() {
            this.pageToActivate = 'deposit';
            this.initDepositList();

            if(this.activateOptions && this.activateOptions.page &&
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
            return true;
        },

        childUpdatePageInstance : function() {
            if(!this.instanceAppended) {
                this.pages[this.pageToActivate].instance = new Y[this.pages[this.pageToActivate].viewClass]({
                    el : this.$el.find('#' + this.pageToActivate),
                    tab_content : this.appDeposit
                });
            }
        },

        childUpdateSidebar : function() {
            var sideBarData = {
                'rek_id':this.options.portal.options.companyRekId,
                'avatar':this.options.portal.options.company_logo_url,
                'own':this.options.portal.options.own_company,
                'authorized':this.options.portal.options.authorized,
                'verified' : this.options.portal.options.verified,
                'sidebarID' : this.options.portal.sidebarID,
                'nonviewed' : Y[this.portletDataProperty].common_data.unviewed_contractors
            };
            this.options.mainSidebar.setMode('some_company', sideBarData);
        },

        childOpenPageTab : function() {
            this.depositTabs.openTabById(this.pageToActivate);
        },

        /* overrides end */

        initRoutes : function() {
            var portal = this.options.portal;

            Y.ApplicationRouter.route(/^deposit\/$/, 'deposit', function (rek_id) {
                portal.activatePortlet('portlet_deposit', {rek_id:rek_id, page : 'deposit'});
            });

            Y.ApplicationRouter.route(/^deposit\/topping-up\/$/, 'topping_up', function (rek_id) {
                portal.activatePortlet('portlet_deposit', {rek_id:rek_id, page : 'topping_up'});
            });

            Y.ApplicationRouter.route(/^deposit\/payments\/$/, 'payments', function (rek_id) {
                portal.activatePortlet('portlet_deposit', {rek_id:rek_id, page : 'payments'});
            });

        },

        initBasicLayout : function() {
            var tabId, tab, CCH, data = {}, thisView = this, portal = this.options.portal, tabdata;

            $.extend(data, {
                brandName : portal.options.brandName,
                categoryText : this.appDeposit.categoryText,
                rekid : this.options.companyRekId,
                verified : this.appDeposit.common_data.verified,
                authorized : this.options.portal.options.authorized,
                own : this.appDeposit.common_data.own_company,
                my_rec_request_status : false,
                their_rec_request_status : false
            });

            CCH = new Y.CurrentCompanyHeader({'data' : data});

            thisView.$el.append(CCH.render().el);

            this.depositTabs = new Y.TabView({
                el : $('#tabs')
            });

            this.depositTabs.bind('tabChanged', this.onMainTabChanged, this);

            for(tabId in this.tabsCollection){
                if(this.tabsCollection.hasOwnProperty(tabId)) {
                    tab = this.tabsCollection[tabId];
                    tabdata = {
                        tabIdName : tabId,
                        tabName :Y.utils.cutLongString(tab.title, 16),
                        tabFullName : tab.title,
                        tabUrl : tab.href
                    };
                    this.depositTabs.addTab(tabdata);
                }
            }

        },

        onMainTabChanged : function(tabId) {
            var url = this.tabsCollection[tabId].routerUrl;
            Y.ApplicationRouter.navigate(url, {trigger : true});
        },

        initDepositList : function() {
            this.depositList = {
                companyRekId : this.options.companyRekId
            };

            this.tabsCollection = {
                deposit : {
                    href : '/deposit/',
                    routerUrl:Y.ApplicationRouter.updateRoute('deposit/'),
                    title : 'Депозит'
                    },
                topping_up : {
                    href : '/deposit/topping-up/',
                    routerUrl:Y.ApplicationRouter.updateRoute('deposit/topping-up/'),
                    title : 'Пополнить счет'
                       },
                payments : {
                    href : '/deposit/payments/',
                    routerUrl:Y.ApplicationRouter.updateRoute('deposit/payments/'),
                    title : 'Оплатить услуги'
                       }
            };
        }
    });

    Y.DepositApplication = DepositApplicationView;
}
