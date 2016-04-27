function x(Y) {
    "use strict";

    Y.PartnersApplicationView = Y.GeneralPortlet.extend({
        portletDataProperty : 'Partners_init',
        portletDataLoadURL : '/contractors/i/',

        own : false,
        ownCompanyRekId : null,
        tabsCollection : null,
        currentRekId : null,
        appSettings : null,

        partnersTabs : null,

        pages : {
            partners_list : {
                viewModule : Y.utils.latestVersionName('tab_partners_list'),
                viewClass : 'TabPartnersList'
            },
            in_reqs : {
                viewModule : Y.utils.latestVersionName('tab_in_reqs'),
                viewClass : 'TabIncomingRequests'
            },
            out_reqs : {
                viewModule : Y.utils.latestVersionName('tab_out_reqs'),
                viewClass : 'TabOutgoingRequests'
            }
        },

        initialize : function() {
            this.ownCompanyRekId = this.options.companyRekId;
            this.initRoutes();
        },

        initRoutes : function() {
            var portal = this.options.portal;
            Y.ApplicationRouter.route(/^contractors\/incoming\/(\?.*)?$/, 'incoming_requests', function() {
                portal.activatePortlet('portlet_partners', { page : 'in_reqs' });
            });
            Y.ApplicationRouter.route(/^contractors\/outgoing\/(\?.*)?$/, 'outgoing_requests', function() {
                portal.activatePortlet('portlet_partners', { page : 'out_reqs' });
            });
        },

        /* overrides from GeneralPortlet */

        hasDataManager : function() {
            return true;
        },

        childInitDataThroughManager : function(callback) {
            var newRekId = this.activateOptions.rek_id || this.ownCompanyRekId, that = this;

            function _initSuccess() {
                that.activateOptions.rerender = (that.currentRekId !== newRekId);
                that.currentRekId = newRekId;
                that.appSettings = that.serverToView(Y[that.portletDataProperty]);
                if(that.appSettings.own) {
                    that.ownCompanyRekId = that.appSettings.rek_id;
                    that.own = true;
                } else {
                    that.own = false;
                }
                callback();
            }

            function _initError(errorLine) {
                Y.Informer.show("Ошибка инициализации контрагентов: " + errorLine, 30);
                callback();
            }

            if(!this.model) {
                this.model = new Y.PartnerManager({ rek_id : newRekId });
            }
            this.model.loadPartnerData(_initSuccess, _initError);
        },

        childInitializePortlet : function() {
            this.pageToActivate = 'partners_list';
            this.initPartnersTabs();

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
                    tabContent : this.appSettings,
                    container : this
                });
            } else {
                this.pages[this.pageToActivate].instance = new Y[this.pages[this.pageToActivate].viewClass]({
                    el : this.$el.find('#' + this.pageToActivate),
                    tabContent : this.appSettings,
                    container : this
                });
            }
        },

        childUpdateSidebar : function() {
            var sideBarData = {
                'rek_id':this.appSettings.rek_id,
                'own':this.appSettings.own,
                'avatar':this.appSettings.company_logo,
                'authorized': this.options.portal.options.authorized,
                'employee_id' : this.appSettings.employee_id,
                'sidebarID' : this.options.portal.sidebarID,
                'verified' : this.appSettings.verified,
                'we_are_partners' : this.appSettings.we_are_partners,
                'nonviewed' : this.model.getNonviewedIncomingCount() // Y[this.portletDataProperty].common_data.unviewed_contractors
            };
            this.options.mainSidebar.setMode('some_company', sideBarData);
        },

        childOpenPageTab : function() {
            this.partnersTabs.openTabById(this.pageToActivate);
        },

        /* overrides end */

        initPartnersTabs : function() {
            var nonViewed = 0;

            this.tabsCollection = [];

            this.tabsCollection.push({
                id : 'partners_list',
                href:'/' + this.appSettings.rek_id + '/contractors/',
                routerUrl:Y.ApplicationRouter.updateRoute(this.appSettings.rek_id + '/contractors/'),
                title: (this.appSettings.own ? "Наши контрагенты" : "Список контрагентов")
            });

            if (this.options.verified && this.appSettings.own) {
                nonViewed = this.model.getNonviewedIncomingCount();
                this.tabsCollection.push({
                    id : 'in_reqs',
                    href:'/contractors/incoming/',
                    routerUrl:Y.ApplicationRouter.updateRoute('contractors/incoming/'),
                    title: "Входящие заявки" + (nonViewed > 0 ? " +" + nonViewed : '')
                });

                this.tabsCollection.push({
                    id : 'out_reqs',
                    href:'/contractors/outgoing/',
                    routerUrl:Y.ApplicationRouter.updateRoute('contractors/outgoing/'),
                    title : "исходящие заявки"
                });
            }
        },

        initBasicLayout : function() {
            var tab, CCH, data = {}, i, tabdata;

            $.extend(data, {
                brandName : this.appSettings.brand_name,
                categoryText : this.appSettings.category_text,
                rekid : this.currentRekId,
                own : this.appSettings.own,
                verified : this.appSettings.verified,
                authorized : this.options.portal.options.authorized,
                my_rec_request_status : this.appSettings.my_rec_request_status,
                their_rec_request_status : this.appSettings.their_rec_request_status,
                they_verified : this.appSettings.they_verified
            });

            CCH = new Y.CurrentCompanyHeader({ 'data' : data });

            this.$el.append(CCH.render().el);

            this.partnersTabs = new Y.TabView({
                el:$('#tabs')
            });

            this.partnersTabs.bind('tabChanged', this.onMainTabChanged, this);

            for (i in this.tabsCollection) {
                if (this.tabsCollection.hasOwnProperty(i)) {
                    tab = this.tabsCollection[i];
                    tabdata = {
                        tabIdName : tab.id,
                        tabName :tab.title,
                        tabFullName : tab.title,
                        tabUrl : tab.href
                    };
                    this.partnersTabs.addTab(tabdata);
                }
            }
        },

        onMainTabChanged:function (tabId) {
            var url, i, tab, that = this;
            for (i in this.tabsCollection) {
                if (this.tabsCollection.hasOwnProperty(i) && this.tabsCollection[i].id === tabId) {
                    tab = that.tabsCollection[i];
                    url = tab.routerUrl;
                    if(this.model.doesNeedReload()) {
                        this.asyncRenewPartnersData(url);
                    } else {
                        Y.ApplicationRouter.navigate(url, { trigger : true });
                    }
                    break;
                }
            }
        },

        asyncRenewPartnersData : function(url) {
            Y.Partners_init = null;
            this.model.loadPartnerData(function() {
                Y.ApplicationRouter.navigate(url, { trigger : true });
            }, function() {
                Y.Informer.show("Ошибка обновления данных о контрагентах");
            });
        },

        serverToView : function(serverData) {
            var viewData = {
                'category_text' : serverData.category_text || '',
                'brand_name' : serverData.brand_name || '',
                'rek_id' : serverData.rek_id || '',
                'own' : serverData.own || false,
                'rek_partners' : this.model.get('rek_partners'), /* serverData.rek_partners || [],*/
                'incoming_requests' : this.model.get('incoming_requests'),
                'outgoing_requests' : this.model.get('outgoing_requests'),
                'company_logo' : serverData.common_data.company_logo_url || '/media/i/default_company_page.png',
                'verified' : serverData.common_data.verified || false,
                'employee_id' : serverData.common_data.employee_id,
                /* 'we_verified' : serverData.common_data.verified || false, */
                'my_rec_request_status' : serverData.common_data.my_rec_request_status,
                'their_rec_request_status' : serverData.common_data.their_rec_request_status,
                'we_are_partners' : serverData.common_data.we_are_contractors || 'no',
                'they_verified' : serverData.common_data.they_verified || false
            };
            return viewData;
        },

        markAsViewed : function(incom_rek_id) {
            var viewedItem, nonviewedCount;
            $.ajax('/contractors/mark_viewed/', {
                success : function(data) {
                    if(data.error) {
                        console.warn("Contractors mark_viewed error in return!");
                    }
                },
                error : function() {
                    console.warn("Contractors mark_viewed error!");
                },
                type : 'POST',
                dataType : 'json',
                data : { rek_id : incom_rek_id },
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
            viewedItem = this.model.getArrayIndexByRekId(incom_rek_id, 'incoming_requests');
            if(viewedItem !== null) {
                this.model.get('incoming_requests')[viewedItem].set('viewed', true);
                this.model.change();
                nonviewedCount = this.model.getNonviewedIncomingCount();
                this.partnersTabs.setStaticTabCaption('in_reqs', "Входящие заявки" +
                        (nonviewedCount > 0 ? " +" + nonviewedCount : ''));
            }
        }
    });
}
