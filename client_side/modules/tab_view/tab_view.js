function x(Y) {
    "use strict";

    var TabView;

    TabView = Backbone.View.extend({
        events : {
            "click div.tab_view_header a" : "onTabClicked"
        },

        commonHeaderItemTemplate : Y.TemplateStore.load('tab-view_tab_header_item'),
        staticHeaderItemTemplate : Y.TemplateStore.load('tab-view_static_header_item'),
        dynamicHeaderItemTemplate : Y.TemplateStore.load('tab-view_dynamic_header_item'),

        pageItemTemplate : Y.TemplateStore.load('tab-view_tab_page'),

        resources : Y.Locales['tab-view'],

        tabs : null,
        tabTimeouts : null,

        currentPage : -1,

        tabViewType : null,

        initialize : function () {
            this.tabs = [];
            this.tabTimeouts = {};
            this.$el.append(Y.TemplateStore.load('tab-view_tab_view'));
            this.tabViewType = (this.options.hasOwnProperty('type') && this.options.type === 'dynamic' ?
                                               'dynamic' : 'static');
            if(this.tabViewType === 'dynamic') {
                this.$el.find('div.tab_view_header').addClass('dynamic');
            }
        },

        addTab : function (tabParams) {
            var tabHeaderItem, headerTemplate, headerData, pageItem;

            if ($.inArray(tabParams.tabUrl, this.tabs) !== -1) {
                Y.log('Tab with id "' + tabParams.tabUrl + '" already in tabview.', 'warn', 'messaging_application');
            } else if(this.tabViewType === 'dynamic' && this.tabs.length > 0) {
                Y.log('Tab with id "' + tabParams.tabUrl + '" must be dynamic - call addDynamicTab', 'warn', 'messaging_application');
            } else {
                this.tabs.push([ tabParams.tabIdName, tabParams.tabUrl, 'static' ]);

                headerTemplate = (this.tabViewType === 'dynamic' ? this.staticHeaderItemTemplate :
                                                                    this.commonHeaderItemTemplate);
                headerData = {
                    name : Y.utils.capitaliseFirstLetter(tabParams.tabName),
                    fullname : (tabParams.tabName === tabParams.tabFullName ? '' : Y.utils.capitaliseFirstLetter(tabParams.tabFullName)),
                    id_tab : tabParams.tabIdName,
                    tab_url : tabParams.tabUrl
                };
                tabHeaderItem = headerTemplate(headerData);
                this.$el.find('div.tab_view_header').append(tabHeaderItem);

                pageItem = this.pageItemTemplate({ id_tab : tabParams.tabIdName });
                this.$el.find('div.tab_view_content').append(pageItem);
                if(this.tabViewType === 'dynamic') {
                    this.$el.find('div.tab_view_content').addClass('chat');
                }
            }
            return this;
        },

        addDynamicTab : function(tabParams) {
            var headerData, pageItem, that = this;
            if($.inArray(tabParams.tabUrl, this.tabs) !== -1) {
                Y.log('Tab with id "' + tabParams.tabUrl + '" already in tabview.', 'warn', 'messaging_application');
            } else if(this.tabViewType === 'dynamic' && this.tabs.length === 0) {
                Y.log('Tab with id "' + tabParams.tabUrl + '" must not be first', 'warn', 'messaging_application');
            } else if(this.tabViewType === 'static') {
                Y.log('Tab with id "' + tabParams.tabUrl + '": cannot add a dynamic tab to a static tab view!', 'warn', 'messaging_application');
            } else {
                this.tabs.push([ tabParams.tabIdName, tabParams.tabUrl, 'dynamic' ]);
                headerData = {
                    name : Y.utils.capitaliseFirstLetter(tabParams.tabName),
                    fullname : (tabParams.tabName === tabParams.tabFullName ? '' : Y.utils.capitaliseFirstLetter(tabParams.tabFullName)),
                    id_tab : tabParams.tabIdName,
                    tab_url : tabParams.tabUrl,
                    loc_tab_close : this.resources.closeTab
                };
                this.$el.find('div.tab_view_header').append(this.dynamicHeaderItemTemplate(headerData));

                $('div.tab_view_header a#link_' + tabParams.tabIdName + ' .close').click(function(e) {
                    that.trigger('closeDynamicTab', tabParams.tabIdName);
                    return false;
                });

                this.$el.find('div.tab_view_header a#link_' + this.tabs[0][0]).addClass('nextarrow');

                pageItem = this.pageItemTemplate({ id_tab : tabParams.tabIdName });
                this.$el.find('div.tab_view_content').append(pageItem);
                if(this.tabViewType === 'dynamic') {
                    this.$el.find('div.tab_view_content').addClass('chat');
                }
            }
            return this;
        },

        openTabById : function (tabId) {
            var that = this, tabContentToActivate;

            if(this.currentPage === -1 || tabId !== this.tabs[this.currentPage][0]) {
                $.each(this.tabs, function(id, currentTab) {
                    var curElement = currentTab[0];
                    if ((tabId === curElement) && (that.currentPage !== id)) {
                        that.currentPage = id;
                        that.resetUnreadState(tabId);
                        tabContentToActivate = that.$el.find('#' + curElement);
                        return false;
                    }
                });

                this.$el.find('.tab_view_header a').removeClass('current');
                this.$el.find('.tab_view_content > div').css('display', 'none');
                this.$el.find('.tab_view_header #link_' + tabId).addClass('current');
                if(tabContentToActivate) {
                    tabContentToActivate.css('display', 'block');
                }
            }
            return this;
        },

        openTabByIndex : function (tabIndex) {
            if (tabIndex < 0 || tabIndex > this.tabs.length - 1) {
                Y.log('Tab with index ' + tabIndex + ' not found in tabview', 'warn', 'messaging_application');
            } else {
                this.openTabById(this.tabs[tabIndex][0]);
            }
            return this;
        },

        onTabClicked : function (eventObject) {
            var elementId = eventObject.currentTarget.pathname, tabId;
            if (elementId[0] !== '/') {
                elementId = '/' + elementId;
            }
            tabId = this.getIdByUrl(elementId);
            if(tabId) {
                this.trigger('tabChanged', tabId);
            } else {
                Y.log('Tab with URL "' + elementId + '" not found in tabview - cannot process click', 'warn', 'tab_view');
            }
            return false;
        },

        removeDynamicTab : function(tabId, activTabId) {
            var idToActivate = null,
                remTabIndex = this.getTabIndexById(tabId);
            if(this.tabs.length < 2) {
                Y.log('Trying to remove a tab "' + tabId + '" from an empty tab view', 'warn', 'messaging_application');
            } else if(remTabIndex === 0) {
                Y.log('Trying to remove static tab with id "' + tabId + '"', 'warn', 'messaging_application');
            } else {
                this.removeTabTimeout(tabId);
                if(activTabId && this.getTabIndexById(activTabId)) {
                    idToActivate = activTabId;
                } else if(this.$el.find('.tab_view_header #link_' + tabId).hasClass('current')) {
                    idToActivate = this.tabs[remTabIndex-1][0];
                }

                this.$el.find('div.tab_view_header #link_' + tabId).remove();
                this.$el.find('div.tab_view_content #' + tabId).remove();
                this.tabs.splice(remTabIndex, 1);
                if(this.tabs.length < 2) {
                    this.$el.find('div.tab_view_header a#link_' + this.tabs[0][0]).removeClass('nextarrow');
                }
                if(idToActivate) {
                    this.currentPage = -1;
                    this.openTabById(idToActivate);
                } else {
                    if(this.currentPage > remTabIndex) {
                        this.currentPage -= 1;
                    }
                }
            }
            return idToActivate;
        },
        getTabIndexById : function(tabId) {
            var i;
            for(i = 0; i < this.tabs.length; i += 1) {
                if(this.tabs[i][0] === tabId) {
                    return i;
                }
            }
            return null;
        },
        getIdByTabIndex : function(tabIndex) {
            return this.tabs[tabIndex][0];
        },
        getIdByUrl : function(tabUrl) {
            var i;
            for(i in this.tabs) {
                if(this.tabs.hasOwnProperty(i)) {
                    if(this.tabs[i][1] === tabUrl) {
                        return this.tabs[i][0];
                    }
                }
            }
            return null;
        },
        getTabContentById : function(tabId) {
            return this.$el.find('.tab_view_content #' + tabId);
        },
        isActiveTab : function(tabId) {
            return this.getTabIndexById(tabId) === this.currentPage;
        },
        highlightTab : function(tabId, unreadNum) {
            var titleElem = this.$el.find('div.tab_view_header #link_' + tabId + ' .tabtitle'),
                hghltTitle = this.$el.find('div.tab_view_header #link_' + tabId + ' .hghlttitle'),
                titleText = titleElem[0].innerHTML;
            titleElem.hide();
            hghltTitle.show();
            hghltTitle.empty();
            hghltTitle.append(titleText + ' +' + unreadNum);

            this.blinkTab(tabId, unreadNum);
        },
        blinkTab : function(tabId, unreadNum) {
            var tabElem = this.$el.find('div.tab_view_header #link_' + tabId), that = this,
                activeFunc, pendingFunc, switchTime;
            function lightTab() {
                tabElem.addClass('unread');
            }
            function dimTab() {
                tabElem.removeClass('unread');
            }

            activeFunc = lightTab;
            pendingFunc = dimTab;
            switchTime = (unreadNum > 10 ? 500 : 830 - unreadNum * 30);

            function blinker() {
                var tmp;
                activeFunc();
                tmp = activeFunc;
                activeFunc = pendingFunc;
                pendingFunc = tmp;
                that.tabTimeouts[tabId] = setTimeout(blinker, switchTime);
            }

            this.removeTabTimeout(tabId);
            this.tabTimeouts[tabId] = setTimeout(blinker, switchTime);
        },
        removeTabTimeout : function(tabId) {
            if(this.tabTimeouts.hasOwnProperty(tabId)) {
                clearTimeout(this.tabTimeouts[tabId]);
                this.tabTimeouts[tabId] = null;
            }
        },
        resetUnreadState : function(tabId) {
            var titleElem = this.$el.find('div.tab_view_header #link_' + tabId + ' .tabtitle'),
                hghltTitle = this.$el.find('div.tab_view_header #link_' + tabId + ' .hghlttitle'),
                tabElem = this.$el.find('div.tab_view_header #link_' + tabId);
            this.removeTabTimeout(tabId);
            hghltTitle.hide();
            titleElem.show();
            tabElem.removeClass('unread');
        },
        setStaticTabCaption : function(tabId, newCaption) {
            this.$el.find('div.tab_view_header #link_' + tabId + ' .tabcaption').empty()
                .append(newCaption);
        }
    });

    Y.TabView = TabView;
}
