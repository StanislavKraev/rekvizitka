function x(Y) {
    "use strict";

    var SearchAppView, searchListDefaultLogoFile = '/media/i/default_company_list.png',
        searchLocales = Y.Locales['search_application'];

    function runSearchStatic(Y, app) {
        var url, query, $searchField = $('div.part-static form input[name=q]'), additionalParams;
        url = Y.ApplicationRouter.updateRoute('/search/');
        query = $searchField.val();
        url += "?q=" + query;
        if (app) {
            additionalParams = app.getAdditionalParams();
            if (additionalParams.length) {
                url += "&" + additionalParams;
            }
            Y.ApplicationRouter.navigate(url, {trigger:true});
        } else {
            Y.ApplicationRouter.navigate(url, {trigger:true});
        }
    }

    function attachStatic(app) {
        var $searchField = $('.search-box form input[name=q]'),
            $searchButton = $('.search-box form input.loupebutton');

        $searchField.unbind('keyup');
        $searchField.keyup(function(eventObj) {
            var code;
            code = eventObj.keyCode || eventObj.which;
            if (code === 13) {
                eventObj.preventDefault();
                runSearchStatic(Y, app);
            }
            $(eventObj.target).trigger('setQueryTextColor');
        });

        $searchField.unbind('setDefaultTextColor');
        $searchField.unbind('setQueryTextColor');
        $searchField.bind('setDefaultTextColor', function() {
            $searchField.css('color', '#aaa');
        });
        $searchField.bind('setQueryTextColor', function() {
            $searchField.css('color', '#333');
        });

        function changeFieldColor(eventObj) {
            if(eventObj.target.value === '') {
                $(eventObj.target).trigger('setDefaultTextColor');
            } else {
                $(eventObj.target).trigger('setQueryTextColor');
            }
        }
        $searchField.unbind('blur');
        $searchField.blur(changeFieldColor);
        $searchField.unbind('change');
        $searchField.change(changeFieldColor);

        $searchButton.off();
        $searchButton.click(function () {
            runSearchStatic(Y, app);
            return false;
        });
    }

    attachStatic();

    SearchAppView = Y.GeneralPortlet.extend({
        paginator:null,
        appSettings:null,
        template:Y.TemplateStore.load('search_application_content'),
        template_item:Y.TemplateStore.load('search_application_result_item'),
        initialized:false,
        locales:searchLocales,
        categories:null,
        loadingNow : false,

        portletDataProperty : 'SearchAppSettings_init',
        portletDataLoadURL : '/search/i/',

        initialize:function () {
            this.initSettings();
            this.categories = [];
            attachStatic(this);
        },

        /* overrides from GeneralPortlet */

        childActivate : function() {
            this.query = decodeURIComponent(Y.utils.getURLparam('q') || "");
            this.loadCatInfo();
            return true;
        },

        getLoadPortletDataURL : function() {
            return this.portletDataLoadURL;
        },

        getLoadPortletDataObject : function() {
            var dataobj = { 'q' : this.query };
            if(this.lastTs && this.isSameRequest()) {
                dataobj.start_ts = this.lastTs;
            }
            $.each(this.categories, function(id, catId) {
                dataobj[catId] = '';
            });
            return dataobj;
        },

        childLoadPortletDataSuccess : function() {
            // Y[this.portletDataProperty] = this.ajaxResponse.data;
            if(this.ajaxResponse.data.error) {
                Y.Informer.show("Ошибка поиска на сервере: " + this.ajaxResponse.data.error);
            } else if(this.ajaxResponse.data.hasOwnProperty('query')) {
                Y[this.portletDataProperty] = this.ajaxResponse.data;
            }
            this.loadingNow = false;
        },

        childLoadPortletDataError : function() {
            Y.Informer.show("Ошибка поиска: " + this.ajaxError.errorThrown, 30);
            this.loadingNow = false;
        },

        ifSameData : function() {
            return this.appSettings.loaded && this.isSameRequest();
        },

        childProcessPortletData : function() {
            this.lastTs = Y[this.portletDataProperty].last_ts;
            this.hasMore = Y[this.portletDataProperty].has_more;
            this.appSettings.results = Y[this.portletDataProperty].results;
        },

        childInitializePortlet : function() {
            this.activateOptions.rerender = !this.isSameRequest();
            this.appSettings.query = this.query;
            this.appSettings.categories = this.categories.slice(0, this.categories.length);
            this.appSettings.categories.sort();
            return true;
        },

        childPageInstanceActivated : function() {
            return true;
        },

        childPrepareDrawPortlet : function() {
            if(this.initialized && this.activateOptions.rerender) {
                this.$el.empty();
                this.preparedUi = null;
                this.tabView = null;
                this.initialized = false;
            }
            return true;
        },

        childUpdatePageInstance : function() {
            setTimeout(this.addUpButton, 0);
            this.$el.find('.search-bar input').focus();
        },

        childOpenPageTab : function() {
        },

        childUpdateSidebar : function() {
            this.options.mainSidebar.setMode('search', { categories : this.categories });
            this.options.mainSidebar.currentModeView.on('company_category_checked', this.onCompanyCategoryChecked, this);
        },

        childDeactivate : function() {
            if(this.infiniteScroll) {
                $(document).unbind('scroll', this.infiniteScroll);
            }
        },

        /* overrides end */

        isSameRequest : function() {
            var newCategories, oldCategories = this.appSettings.categories.join(' ');
            this.categories.sort();
            newCategories = this.categories.join(' ');
            return (this.query === this.appSettings.query && newCategories === oldCategories);
        },

        loadCatInfo : function() {
            var cat_small = Y.utils.getURLparam('small'),
                cat_startup = Y.utils.getURLparam('startup'),
                cat_social_project = Y.utils.getURLparam('social_project');
            this.categories = [];
            if (cat_small !== null) {
                this.categories.push('small');
            }
            if (cat_startup !== null) {
                this.categories.push('startup');
            }
            if (cat_social_project !== null) {
                this.categories.push('social_project');
            }
        },

        getAdditionalParams:function() {
            var params = [];
            $.each(this.categories, function(id, val) {
                params.push(val);
            });
            return params.join('&');
        },

        replaceResults:function (data, append) {
            this.lastTs = data.last_ts;
            this.hasMore = data.has_more;
            this.fillResultBlock(data.results, append);
        },

        onResultLinkClicked:function (url) {
            Y.ApplicationRouter.navigate(url, {trigger:true});
        },

        setFields:function (query) {
            this.$el.find('div.search-bar input').val(query);
            $('div.part-static form input[name=q]').val(query);
            if(!query) {
                this.$el.find('div.search-bar input').trigger('setDefaultTextColor');
                $('div.part-static form input[name=q]').trigger('setDefaultTextColor');
            } else {
                this.$el.find('div.search-bar input').trigger('setQueryTextColor');
                $('div.part-static form input[name=q]').trigger('setQueryTextColor');
            }
        },

        updateResults:function() {
            var that = this;
            this.loadingNow = true;
            this.loadPortletDataFromServer(function() {
                that.replaceResults(that.ajaxResponse.data, true);
            });
        },

        initBasicLayout:function () {
            var inputTimer, thisView = this,
                inputElement;

            this.$el.append(this.template({ search_placeholder : this.locales.defaultSearchFieldText }));

            this.fillResultBlock(this.appSettings.results);

            this.$el.find('div.search-result').on('click', 'a', function (eventObject) {
                if (eventObject && eventObject.currentTarget && eventObject.currentTarget.pathname) {
                    thisView.onResultLinkClicked(eventObject.currentTarget.pathname);
                }
                return false;
            });

            inputElement = this.$el.find('div.search-bar input');
            inputElement.unbind('setDefaultTextColor');
            inputElement.unbind('setQueryTextColor');
            inputElement.bind('setDefaultTextColor', function() {
                inputElement.css('color', '#aaa');
            });
            inputElement.bind('setQueryTextColor', function() {
                inputElement.css('color', '#333');
            });

            inputElement.keyup(function (eventObj) {
                var code = eventObj.keyCode || eventObj.which, query;

                if(code > 111 && code < 124) {
                    if (inputTimer) {
                        clearTimeout(inputTimer);
                        inputTimer = null;
                    }
                    return;
                }

                inputElement.trigger('setQueryTextColor');

                query = inputElement.val();
                thisView.query = query;
                if (code === 13) {
                    if (inputTimer) {
                        clearTimeout(inputTimer);
                        inputTimer = null;
                    }

                    eventObj.preventDefault();
                    this.query = query;
                    Y.ApplicationRouter.navigate(thisView.makeUrl(), {trigger:true});
                    return;
                }

                if (inputTimer) {
                    clearTimeout(inputTimer);
                    inputTimer = null;
                }

                inputTimer = setTimeout(function () {
                    inputTimer = null;
                    Y.ApplicationRouter.navigate(thisView.makeUrl(), {trigger:true});
                }, 1000);
            });

            inputElement.blur(function(eventObj) {
                if(inputElement.val() === '') {
                    inputElement.trigger('setDefaultTextColor');
                }  else {
                    inputElement.trigger('setQueryTextColor');
                }
            });

            this.infiniteScroll = function () {
                var docTop, elTop, top;
                thisView.placeUpButton();
                if(thisView.hasMore && !thisView.loadingNow) {
                    top = $(document).scrollTop();
                    docTop = top + $(window).height();
                    elTop = thisView.$el.find('.search-result li:last').position().top;
                    if (docTop > elTop) {
                        thisView.loadMoreResults();
                    }
                }
            };

            $(document).unbind('scroll', this.infiniteScroll);
            $(document).scroll(this.infiniteScroll);

            this.setFields(this.appSettings.query);
        },

        placeUpButton : function() {
            var docTop, top, docHeight, footerHeight;
            top = $(document).scrollTop();
            docTop = top + $(window).height();
            footerHeight = 50;
            if (top > 700) {
                docHeight = $(document).height();
                $('.search-sidebar .search-go-up').fadeIn(300);
                if (docHeight - docTop < footerHeight) {
                    $('.search-sidebar .search-go-up').css({bottom: 8 + footerHeight - (docHeight - docTop)});
                } else {
                    $('.search-sidebar .search-go-up').css({bottom: 8});
                }
            } else {
                $('.search-sidebar .search-go-up').fadeOut(300);
            }
        },

        addUpButton : function() {
            var template = '<a class="search-go-up" style="display: none">Наверх</a>', button$;
            $('a.search-go-up').remove();
            $('.search-sidebar').append(template);
            button$ = $('.search-sidebar .search-go-up');

            function repositionButton() {
                button$.css({left:$('#left-sidebar').offset().left + $('#left-sidebar').width() - button$.width() + 13});
            }
            button$.click(function() {
                button$.hide();
                $(window).scrollTop(0);
            });
            $(window).resize(function() {
                repositionButton();
            });
            repositionButton();
        },

        loadMoreResults : function() {
            this.updateResults();
        },

        fillResultBlock : function(results, append) {
            var itemId, dataItem, dataElement, resString = '';
            if (results.length) {
                this.$el.find('div.search-result').show();
                this.$el.find('div.search-not-found').hide();
                this.$el.find('div.search-result h3').text(this.locales.resultlist);
                for (itemId in results) {
                    if (results.hasOwnProperty(itemId)) {
                        dataItem = results[itemId];
                        dataElement = {
                                   'logo' : dataItem.logo || searchListDefaultLogoFile,
                                   'bname' : dataItem.bname || "",
                                   'company_url' : dataItem.company_url || "",
                                   'kind_of_activity' : dataItem.kind_of_activity || ""
                        };
                        resString += this.template_item(dataElement);
                    }
                }
                if (!append) {
                    this.$el.find('div.search-result ul').empty();
                }
                this.$el.find('div.search-result ul').append(resString);
                this.placeUpButton();
            } else if (!append) {
                this.$el.find('div.search-result').hide();
                this.$el.find('div.search-not-found').show();
                this.$el.find('div.search-not-found p').text(this.locales.empty_resultlist);
            }
        },

        initSettings:function () {
            if (Y.SearchAppSettings_init) {
                this.appSettings = Y.SearchAppSettings_init;
                this.appSettings.loaded = true;
                this.appSettings.categories = this.appSettings.categories || [];
                this.appSettings.categories.sort();
            } else {
                this.appSettings = {
                    'query' : "",
                    'page' : 0,
                    'results' : [],
                    'categories' : []
                };
            }
            this.appSettings.count = this.appSettings.results.length;
        },

        makeUrl : function() {
            var url = '/search/', params = [];
            if (this.query.length) {
                params.push('q=' + this.query);
            }
            params = params.concat(this.categories);
            if (params.length) {
                url += '?' + params.join('&');
            }
            return url;
        },

        onCompanyCategoryChecked : function(categoryId, state) {
            var newState=!!state, oldState,
                index = $.inArray(categoryId, this.categories),
                newSearchUrl;
            oldState = index !== -1;

            if (newState !== oldState) {
                if (newState) {
                    this.categories.push(categoryId);
                } else {
                    this.categories.splice(index, 1);
                }
                newSearchUrl = this.makeUrl();
                Y.ApplicationRouter.navigate(newSearchUrl, {trigger:true});
            }
        }
    });

    Y.SearchApplication = SearchAppView;
}
