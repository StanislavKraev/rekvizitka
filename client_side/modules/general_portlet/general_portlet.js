function x(Y) {
    "use strict";

    Y.GeneralPortlet = Backbone.View.extend({
        /* overridable data */
        portletDataProperty : 'General_init',    // replace with real name like 'Chat_init', 'Recommendations_init'
        portletDataLoadURL : '/general/i/',    // what to call to load portlet data
        portletInit : null,
        active : false,
        ajaxResponse : null,
        ajaxError : null,
        ajaxXhr : null,

        /* methods of the activating/deactivating mechanism -
         * do not override without proper reasons
         * it is called from the main_portal
         */

        activate : function(options) {
            var that = this;
            this.activateOptions = options;
            function _initPortletTail() {
                that.activatePortletTail();
            }

            if(this.childActivate()) {
                this.initPortletData(_initPortletTail);
            }
        },
        initPortletData : function(tailCall) {
            if(this.hasDataManager()) {
                this.childInitDataThroughManager(tailCall);
            } else {
                if(Y.hasOwnProperty(this.portletDataProperty) && this.ifSameData()) {
                    this.childProcessPortletData();
                    tailCall();
                } else {
                    this.loadPortletDataFromServer(tailCall);
                }
            }
        },
        loadPortletDataFromServer : function(tailCall) {
            var that = this;
            if(this.ajaxXhr) {
                this.ajaxXhr.abort();
            }
            this.ajaxXhr = $.ajax(this.getLoadPortletDataURL(), {
                success : function(data, textStatus, jqXHR) {
                    that.ajaxResponse = {
                        data : data,
                        textStatus : textStatus,
                        jqXHR : jqXHR
                    };
                    that.childLoadPortletDataSuccess();
                    that.childProcessPortletData();
                    tailCall();
                },
                error : function(jqXHR, textStatus, errorThrown) {
                    that.ajaxError = {
                        jqXHR : jqXHR,
                        textStatus : textStatus,
                        errorThrown : errorThrown
                    };
                    that.childLoadPortletDataError();
                },
                type : 'GET',
                dataType : 'json',
                data : this.getLoadPortletDataObject(),
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },
        activatePortletTail : function() {
            var that = this;
            function _activatePageTail() {
                that.activatePageTail();
            }
            if(this.childInitializePortlet()) {
                this.activatePage(_activatePageTail);
            }
        },
        activatePage : function(tailCall) {
            if(this.childPageInstanceActivated()) {
                tailCall();
            } else {
                Y.use(this.getClassModuleName(), tailCall);
            }
        },
        activatePageTail : function() {
            this.deactivatePrevious();
            if(this.childPrepareDrawPortlet()) {
                this.drawPortlet();
            }
            this.childUpdatePageInstance();
            this.childUpdateSidebar();
            this.childOpenPageTab();
            this.active = true;
        },
        deactivatePrevious : function() {
            if(this.hasOwnProperty('activateOptions') &&
                this.activateOptions.deactivatePrevious) {
                this.activateOptions.deactivatePrevious();
            }
        },
        deactivate : function() {
            this.childDeactivate();
            if(this.ajaxXhr) {
                this.ajaxXhr.abort();
                this.ajaxXhr = null;
            }
            this.preparedUi = this.$el.children().detach();
            this.active = false;
        },
        drawPortlet : function() {
            if(!this.initialized) {
                this.initBasicLayout();
                this.initialized = true;
            } else {
                if(this.preparedUi) {
                    this.$el.append(this.preparedUi);
                    // this.preparedUi = null;
                } else {
                    this.$el.empty();
                    this.initBasicLayout();
                }
                this.preparedUi = null;
            }
        },

        /* ovverridables - insert methods with real code in your child portlet */

        getLoadPortletDataURL : function() {
            throw new Error("Override getLoadPortletDataURL method");
        },
        childInitializePortlet : function() {
            throw new Error("Override childInitializePortlet method");
        },
        childPageInstanceActivated : function() {
            throw new Error("Override childPageInstanceActivated method");
        },
        getClassModuleName : function() {
            throw new Error("Override getClassModuleName method");
        },
        childPrepareDrawPortlet : function() {
            throw new Error("Override childPrepareDrawPortlet method");
        },
        childUpdatePageInstance : function() {
            throw new Error("Override childUpdatePageInstance method");
        },
        childOpenPageTab : function() {
            throw new Error("Override childOpenPageTab method");
        },
        /* unnecessary overrides - not all portlets have to override them */
        hasDataManager : function() {
            return false;
        },
        ifSameData : function() {
            return true;
        },
        childActivate : function() {
            return true;
        },
        childLoadPortletDataSuccess : function() {
            Y[this.portletDataProperty] = this.ajaxResponse.data;
        },
        childProcessPortletData : function() {
            this.portletInit = Y[this.portletDataProperty];
        },
        childUpdateSidebar : function() {
        },
        childLoadPortletDataError : function() {
        },
        getLoadPortletDataObject : function() {
        },
        childInitDataThroughManager : function() {
        },
        childDeactivate : function() {
        }
    });
}
