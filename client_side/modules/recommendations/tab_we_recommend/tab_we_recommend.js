function x(Y) {
    "use strict";

    var AcceptedListView, NotAcceptedListView, TabWeRecommend;

    // options must contain:
    // - parentView
    // - data: {rek_id, brand_name, logo, kind_of_activity, request_id}
    NotAcceptedListView = Backbone.View.extend({
        tagName:"li",
        template_li:Y.TemplateStore.load('tab_we_recommend_li'),
        events:{
            "click a.accept":"onAccept",
            "click a.decline":"onDecline"
        },
        requestId : '',
        defaultCompanyList:'/media/i/default_company_recommendations.png',

        initialize : function() {
            this.parentView = this.options.parentView;
            this.requestId = this.options.data.request_id;
        },

        onAccept:function () {
            var thisView = this, url = '/recommendations/accept/' + this.requestId + '/';

            function onSendAjaxSuccess(data) {
                if (data.error) {
                    Y.Informer.show("Не удалось рекомендовать компанию", 10);
                } else {
                    thisView.parentView.moveCompanyToAcceptedList(thisView);
                }
            }

            $.ajax(url, {
                success:onSendAjaxSuccess,
                error:function () {
                    Y.Informer.show("Не удалось рекомендовать компанию", 10);
                },
                type:'POST',
                data:{},
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });

            return false;
        },

        onDecline:function () {
            var thisView = this;

            function onSendAjaxSuccess(data) {
                if (data.error) {
                    Y.Informer.show(data.error_message, 10);
                } else {
                    thisView.parentView.declineCompanyRequest(thisView);
                }
            }

            $.ajax('/recommendations/decline/' + this.options.data.request_id + '/', {
                success:onSendAjaxSuccess,
                error:function () {
                    Y.Informer.show('Ошибка при отказе рекомендации!', 10);
                },
                type:'POST',
                data:{'_id':this.options.data.rek_id},
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
            return false;
        },

        render:function () {
            this.options.data.logo = this.options.data.logo || this.defaultCompanyList;
            this.$el.append(this.template_li(this.options.data));
            this.$el.on('click', 'a.arrow', this, function() {
                $(this).closest('.exp-details').toggleClass('closed').toggleClass('open');
            });
            return this;
        },

        getDataForAcceptedList:function() {
            return {
                data: {
                    rek_id : this.options.data.rek_id,
                    brand_name : this.options.data.brand_name
                }
            };
        }
    });

    // options must contain:
    // - data: rek_id, brand_name
    AcceptedListView = Backbone.View.extend({
        template_accepted_list:Y.TemplateStore.load('tab_we_recommend_accepted_list'),

        render:function () {
            this.$el.append(this.template_accepted_list(this.options.data));
            return this;
        }
    });

    // options must contain:
    // - el
    // - receivedNotAccepted: [{rek_id, brand_name, logo, kind_of_activity, request_id}]
    // - receivedAccepted: [{rek_id, brand_name}]
    // - own (company)
    TabWeRecommend = Backbone.View.extend({
        template:Y.TemplateStore.load('tab_we_recommend_content'),
        template_ul:Y.TemplateStore.load('tab_we_recommend_ul'),

        acceptedList:[],
        notAcceptedList:[],
        receivedNotAccepted:[],
        receivedAccepted:[],
        own:false,

        initialize:function () {
            var i, optionsData = this.options.tabContent;
            this.own = optionsData.own;

            if (this.own) {
                for (i in optionsData.receivedNotAccepted) {
                    if (optionsData.receivedNotAccepted.hasOwnProperty(i)){
                        this.receivedNotAccepted.push($.extend(true, {}, optionsData.receivedNotAccepted[i]));
                    }
                }
            }

            for (i in optionsData.receivedAccepted) {
                if (optionsData.receivedAccepted.hasOwnProperty(i)){
                    this.receivedAccepted.push($.extend(true, {}, optionsData.receivedAccepted[i]));
                }
            }
            this.initLayout();
        },

        initLayout:function() {
            var i, view, arr = [],
                received_not_accepted = '',
                received_accepted = '',
                receivedNotAcceptedLen,
                receivedAcceptedLen;

            this.$el.empty();

            receivedNotAcceptedLen = this.receivedNotAccepted.length;
            receivedAcceptedLen = this.receivedAccepted.length;

            if (this.own) {
                if (receivedNotAcceptedLen) {
                    received_not_accepted = 'Просят дать рекомендацию: ' +
                        receivedNotAcceptedLen + ' ' + Y.utils.morph('компания', receivedNotAcceptedLen, 'i');
                }
            } else if (!receivedAcceptedLen) {
                received_not_accepted = 'Компания еще никому не дала своих рекомендаций';
            }

            if (receivedAcceptedLen) {
                received_accepted = 'Мы уже дали рекомендацию ' +
                    receivedAcceptedLen + ' ' + Y.utils.morph('компания', receivedAcceptedLen, 'd');
            }

            this.$el.append(this.template({
                'not_accepted_header':received_not_accepted,
                'accepted_header':received_accepted,
                'own':this.own
            }));

            if (receivedNotAcceptedLen || receivedAcceptedLen) {
                this.$el.find('p.intro-text').after('<hr>');
            }

            if (this.own) {
                if (receivedNotAcceptedLen) {
                    for (i in this.receivedNotAccepted) {
                        if (this.receivedNotAccepted.hasOwnProperty(i)) {

                            view = new NotAcceptedListView({
                                'data':this.receivedNotAccepted[i],
                                'parentView':this
                            });

                            this.$el.find('ul.list').append(view.render().el);
                            this.notAcceptedList.push(view);
                        }
                    }
                }
            }

            this.$el.find('.accepted-list').empty();
            this.acceptedList = [];
            if (this.receivedAccepted.length) {
                for (i in this.receivedAccepted) {
                    if (this.receivedAccepted.hasOwnProperty(i)) {

                        view = new AcceptedListView({
                            'data':this.receivedAccepted[i]
                        });

                        arr.push(view.render().el.innerHTML);
                        this.acceptedList.push(view);
                    }
                }
                this.$el.find('.accepted-list').append(arr.join(', '));
            }

            function loadAjaxUrl(eventObject) {
                var url = eventObject.currentTarget.pathname + eventObject.currentTarget.search;
                Y.ApplicationRouter.navigate(url, {trigger:true});
                return false;
            }

            $('#we_recommend ul.company').on('click', 'td.column1 a, td.column2 a', this, loadAjaxUrl);
            $('#accepted-list-container').on('click', 'a', this, loadAjaxUrl);
        },

        moveCompanyToAcceptedList:function (notAcceptedView) {
            var index, view;

            for (index = 0; index < this.notAcceptedList.length; index += 1) {
                if (notAcceptedView === this.notAcceptedList[index]) {
                    notAcceptedView.$el.remove();
                    view = new AcceptedListView(this.notAcceptedList[index].getDataForAcceptedList());
                    this.notAcceptedList.splice(index, 1);
                    this.acceptedList.push(view);
                    this.updateHeadersAndLists();
                    break;
                }
            }
        },

        updateHeadersAndLists : function() {
            var acceptedHeaderText = '', receivedAcceptedLen,
                i, viewRenders=[], requestedHeaderText, receivedNotAcceptedLen;

            for (i in this.acceptedList) {
                if (this.acceptedList.hasOwnProperty(i)) {
                    viewRenders.push(this.acceptedList[i].render().el.innerHTML);
                }
            }
            this.$el.find('.accepted-list').html(viewRenders.join(', '));
            this.$el.find('.accepted-list div a').unwrap();

            receivedAcceptedLen = this.acceptedList.length;
            if (receivedAcceptedLen > 0) {
                acceptedHeaderText = 'Мы уже дали рекомендацию ' +
                    receivedAcceptedLen + ' ' + Y.utils.morph('компания', receivedAcceptedLen, 'd');
            }
            this.$el.find('#accepted_header_title').text(acceptedHeaderText);

            receivedNotAcceptedLen = this.notAcceptedList.length;
            if (receivedNotAcceptedLen > 0) {
                requestedHeaderText = 'Просят дать рекомендацию: ' +
                    receivedNotAcceptedLen + ' ' + Y.utils.morph('компания', receivedNotAcceptedLen, 'i');
                this.$el.find('#requested_header_title').text(requestedHeaderText);
            } else {
                this.$el.find('#requested_header_title').remove();
            }
        },

        declineCompanyRequest:function (declinedView) {
            var index, view;

            for (index = 0; index < this.notAcceptedList.length; index += 1) {
                if (declinedView === this.notAcceptedList[index]) {
                    declinedView.$el.remove();
                    this.notAcceptedList.splice(index, 1);
                    this.updateHeadersAndLists();
                    break;
                }
            }
        },

        // newData must contain:
        // - el
        // - receivedNotAccepted: [{rek_id, brand_name, logo, kind_of_activity, request_id}]
        // - receivedAccepted: [{rek_id, brand_name}]
        setData:function (newData) {
            var i, optionsData = newData.tabContent;
            this.el = newData.el;
            this.$el = $(this.el);

            this.acceptedList = [];
            this.notAcceptedList = [];
            this.receivedNotAccepted = [];
            this.receivedAccepted = [];
            this.own = optionsData.own;

            if (this.own) {
                for (i in optionsData.receivedNotAccepted) {
                    if (optionsData.receivedNotAccepted.hasOwnProperty(i)){
                        this.receivedNotAccepted.push($.extend(true, {}, optionsData.receivedNotAccepted[i]));
                    }
                }
            }

            for (i in optionsData.receivedAccepted) {
                if (optionsData.receivedAccepted.hasOwnProperty(i)){
                    this.receivedAccepted.push($.extend(true, {}, optionsData.receivedAccepted[i]));
                }
            }

            this.initLayout();
        }
    });

    Y.TabWeRecommend = TabWeRecommend;
}