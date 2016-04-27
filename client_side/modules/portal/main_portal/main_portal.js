function x(Y) {
    "use strict";

    var MainPortalView;

    MainPortalView = Backbone.View.extend({
        header:null,
        sidebar:null,
        profileAppPortlet:null,
        messagingAppPortlet:null,
        currentPortlet:null,
        rekID:'',
        profileUrl:'',
        appSettings:null,
        prevCursor : null,

        initialize:function () {

            this.initPortlets();

            var portal = this,
                main_portal_init = this.options.main_portal_init,
                rekID = this.options.companyRekId;

            this.profileUrl = "/" + this.options.companyRekId + '/profile/';

            this.myProfileUrl = "/" + this.options.ownCompanyRekId + '/profile/';

            Y.GlobalNotifier.start(this.options.notifications);

            /* HEADER */

            this.header = new Y.MainHeader({
                el:portal.options.header,
                brandName:portal.options.ownBrandName,
                auth:portal.options.authorized,
                csrf:portal.options.csrf_token,
                employeeProfileUrl:portal.myProfileUrl // todo: after employee are implemented - change url to appropriate one
            });

            /* SIDEBAR */

            this.sidebar = this.initSidebar();

            this.sidebar.bind('sidebarLinkClicked', this.sidebarAction, this);

            /* MAIN PORTAL INIT */

            if (main_portal_init) {
                Y.use(main_portal_init.mainPortlet, function (Y, result) {
                    var initialPage, portletId, portlet;

                    if (!result.success) {
                        Y.log('Load failure: ' + result.msg, 'warn', 'Example');
                    } else {

                        initialPage = new Y[main_portal_init.mainPortletClass]({
                            el:portal.options.centerBlock,
                            companyRekId:rekID,
                            verified:portal.options.verified,
                            mainSidebar:portal.sidebar,
                            portal:portal
                        });

                        portal.currentPortlet = initialPage;

                        for (portletId in portal.portlets) {
                            if (portal.portlets.hasOwnProperty(portletId)) {
                                portlet = portal.portlets[portletId];
                                if (portlet.mainModuleName === main_portal_init.mainPortlet &&
                                    portlet.mainClassName === main_portal_init.mainPortletClass) {
                                    portlet.instance = initialPage;
                                    portal.sidebarID = portal.portlets[portletId].sidebarID;
                                }
                            }
                        }

                        portal.initRoutes();
                    }
                });
            } else {
                this.initRoutes();
            }

            this.initBottomLinks();
        },

        initBottomLinks:function () {
            $('footer table').on('click', 'a', function (e) {
                var url = e.currentTarget.pathname + e.currentTarget.search;

                Y.ApplicationRouter.navigate(url, {trigger:true});

                return false;
            });
        },

        initTopHeaderLinks:function () {
            $('div.part-static td.sub-menu-item').on('click', 'a', function (eventObject) {
                var url = eventObject.currentTarget.pathname + eventObject.currentTarget.search;

                Y.ApplicationRouter.navigate(url, {trigger:true});

                return false;
            });
        },

        initPortlets:function () {
            this.portlets = {
                'profile_about':{
                    mainModuleName:Y.utils.latestVersionName('profile_application'),
                    mainClassName:'ProfileApplication',
                    sidebarID:'profile',
                    activationExtraOptions:{
                        page:"profile"
                    }
                },

                'search':{
                    mainModuleName:Y.utils.latestVersionName('search_application'),
                    mainClassName:'SearchApplication',
                    sidebarID:'search'
                },

                'portlet_settings':{
                    mainModuleName:Y.utils.latestVersionName('settings_application'),
                    mainClassName:'ProfileSettings',
                    sidebarID:'settings',
                    activationExtraOptions:{
                        page:"settings"
                    }
                },

                'portlet_recommendations':{
                    mainModuleName:Y.utils.latestVersionName('recommendations_application'),
                    mainClassName:'RecommendationsApplication',
                    sidebarID:'our_proposers',
                    activationExtraOptions:{
                        page:"verification"
                    }
                },

                'portlet_deposit':{
                    mainModuleName:Y.utils.latestVersionName('deposit_application'),
                    mainClassName:'DepositApplication',
                    sidebarID:'deposit',
                    activationExtraOptions:{
                        page:"deposit"
                    }
                },

                'portlet_feedback':{
                    mainModuleName:Y.utils.latestVersionName('feedback_application'),
                    mainClassName:'FeedbackApplication',
                    sidebarID:'feedback',
                    activationExtraOptions:{
                        page:"feedback"
                    }
                },

                'portlet_chat' : {
                    mainModuleName :Y.utils.latestVersionName('chat_application'),
                    mainClassName : 'ChatApplicationView',
                    sidebarID:'chat',
                    activationExtraOptions : {
                        page : 'dialog_list'
                    },
                    verifiedOnly : true,
                    verifiedOnlyMessage : '<a href="/verification/">Пройдите верификацию</a>, чтобы иметь возможность отправлять сообщения'
                },

                'portlet_partners' : {
                    mainModuleName : Y.utils.latestVersionName('partners_application'),
                    mainClassName : 'PartnersApplicationView',
                    sidebarID:'partners',
                    activationExtraOptions : {
                        page : 'partners_list'
                    }
                }
            };
        },

        sidebarAction:function (linkObj) {
            Y.ApplicationRouter.navigate(Y.ApplicationRouter.updateRoute(linkObj.linkURL), {trigger:true});
        },

        initRoutes:function () {
            var app = this, rootUrl = Y.ApplicationRouter.rootUrl;

            Y.ApplicationRouter.route(/^([0-9A-Z]+)\/$/, 'rek_core', function (rek_id) {
                Y.ApplicationRouter.navigate(Y.ApplicationRouter.updateRoute(rek_id + '/profile/'), {replace:true, trigger:true});
            });

            // todo: group routes and put them into "portlets" map
            Y.ApplicationRouter.route(/^([0-9A-Z]+)\/profile\/$/, 'profile_num', function (rek_id) {
                app.activatePortlet('profile_about', {rek_id:rek_id});
            });

            Y.ApplicationRouter.route(/^search\/(.*)/, 'search', function (params) {
                app.activatePortlet('search', {searchString:params});
            });

            Y.ApplicationRouter.route(/^deposit\/$/, 'deposit', function () {
                app.activatePortlet('portlet_deposit', {page:'deposit'});
            });

            Y.ApplicationRouter.route(/^feedback\/$/, 'feedback', function () {
                app.activatePortlet('portlet_feedback', {page:'feedback'});
            });

            Y.ApplicationRouter.route(/^settings\/$/, 'settings', function () {
                app.activatePortlet('portlet_settings', {page:'settings'});
            });

/* RECOMMENDATIONS */

            Y.ApplicationRouter.route(/^([0-9A-Z]+)\/our_proposers\/$/, 'our_proposers', function (rek_id) {
                app.activatePortlet('portlet_recommendations', {rek_id:rek_id, page:'our_proposers'});
            });

            Y.ApplicationRouter.route(/^([0-9A-Z]+)\/we_recommend\/$/, 'we_recommend', function (rek_id) {
                app.activatePortlet('portlet_recommendations', {rek_id:rek_id, page:'we_recommend'});
            });

            Y.ApplicationRouter.route(/^verification\/$/, 'verification', function () {
                app.activatePortlet('portlet_recommendations', {page:'verification'});
            });

            Y.ApplicationRouter.route(/^invites\/$/, 'invites', function () {
                app.activatePortlet('portlet_recommendations', {page:'invites'});
            });

            /* CHAT */

            Y.ApplicationRouter.route(/^chat\/(\?.*)?$/, 'chat', function () {
                app.activatePortlet('portlet_chat', { page : 'dialog_list' });
            });
            Y.ApplicationRouter.route(/^chat\/dialog\/([0-9A-Za-z]+)\/$/, 'dialog', function (dialogId) {
                app.activatePortlet('portlet_chat', { dialogId : dialogId, page : 'dialog' });
            });
            Y.ApplicationRouter.route(/^chat\/start_dialog\/([0-9A-Za-z]+)\/$/, 'start_dialog', function (corrId) {
                app.activatePortlet('portlet_chat', { corrId : corrId, page : 'start_dialog' });
            });

            /*
            Y.ApplicationRouter.route(this.options.companyRekId + '/set-password/', 'set-password', function () {
            app.activatePortlet('settings');
            });
            */

            Y.ApplicationRouter.route(/^([0-9A-Z]+)\/contractors\/(\?.*)?$/, 'partners', function (rek_id) {
                app.activatePortlet('portlet_partners', { rek_id : rek_id, page : 'partners_list' });
            });

            if (Y.ApplicationRouter.notPushState) {
                Y.ApplicationRouter.start();
            } else {
                Backbone.history.start({pushState:true, root:rootUrl});
            }
        },

        activatePortlet:function (portletId, activationOptions) {
            var portal = this,
                portletData,
                mainModuleName,
                portletActivationOptions;

            portal.sidebarID = this.portlets[portletId].sidebarID;

            portletData = this.portlets[portletId];

            if (!portletData) {
                console.error('Could not found portlet with id ' + portletId);
                return;
            }

            mainModuleName = portletData.mainModuleName;

            portletActivationOptions = {};

            if (portletData.activationExtraOptions) {
                $.extend(portletActivationOptions, portletData.activationExtraOptions);
            }

            if (activationOptions) {
                $.extend(portletActivationOptions, activationOptions);
            }

            if (portletData.verifiedOnly && !portal.options.verified) {
                Y.VerifiedOnlyMessage(portletData.verifiedOnlyMessage);
                return;
            }

            if (!portletData.instance) {
                Y.use(mainModuleName, function (Y) {
                    portletData.instance = new Y[portletData.mainClassName]({
                        el:portal.options.centerBlock,
                        companyRekId:portal.options.companyRekId,
                        verified:portal.options.verified,
                        mainSidebar:portal.sidebar,
                        portal:portal
                    });

                    portal.switchPortlet(portletData.instance, portletActivationOptions);
                });
            } else {
                portal.switchPortlet(portletData.instance, portletActivationOptions);
            }
        },

        switchPortlet:function (portlet, portletActivationOptions) {
            var deactivCallback,
                that = this,
                prevPortlet = this.currentPortlet;

            deactivCallback = function() {
            };

            if (this.currentPortlet) {
                deactivCallback = function() {
                    prevPortlet.deactivate();
                };
            }

            portlet.activate($.extend(portletActivationOptions, {
                deactivatePrevious : deactivCallback
            }));

            this.currentPortlet = portlet;
        },

        initSidebar:function () {
            var createMainSideBar,
                thisView = this,
                sidebarID, portletID;

            for (portletID in this.portlets) {
                if (this.portlets.hasOwnProperty(portletID)) {

                    if (this.portlets[portletID].mainModuleName === this.options.main_portal_init.mainPortlet &&
                        this.portlets[portletID].mainClassName === this.options.main_portal_init.mainPortletClass) {
                        sidebarID = this.portlets[portletID].sidebarID;
                    }
                }
            }

            createMainSideBar = new Y.MainSideBar({
                el:thisView.options.sidebar
            });

            switch (thisView.options.sidebar_mode) {

                case 'feedback':
                    break;

                case 'some_company':
                case '':
                    createMainSideBar.setMode('some_company', {
                        'rek_id':thisView.options.companyRekId,
                        'employee_id':thisView.options.employee_id,
                        'sidebarID':sidebarID,
                        'avatar':thisView.options.company_logo_url || '',
                        'own':thisView.options.own_company || false,
                        'verified':thisView.options.verified || false,
                        'authorized':thisView.options.authorized,
                        'contractors':thisView.options.contractors || []});
                    break;

                case 'search':
                    createMainSideBar.setMode('search', {});
                    break;
            }
            return createMainSideBar;
        }
    });

    Y.MainPortal = MainPortalView;

    Y.VerifiedOnlyMessage = function(message, needRollback) {
        var rollback = (needRollback === null ? true : !!needRollback);
        Y.Modalbox.showSimple(message || Y.Locales['main_portal'].verified_only_message,
            [ { bcaption : 'Закрыть', bstyle : "simple", callback : function() {
                if(rollback) {
                    window.history.go(-1);
                }
            } } ], 300);
    };
}
