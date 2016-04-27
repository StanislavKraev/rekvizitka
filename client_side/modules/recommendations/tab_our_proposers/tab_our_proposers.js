function x(Y) {
    "use strict";

    // options must contain:
    // el,
    // tabContent : {
    //                  sentAcceptedList : [{brand_name, rek_id, logo, kind_of_activity}]
    // }
    Y.TabOurProposers = Backbone.View.extend({
        sentAcceptedList:[],
        template:Y.TemplateStore.load('tab_our_proposers_content'),
        template_ul:Y.TemplateStore.load('tab_our_proposers_ul'),
        template_li:Y.TemplateStore.load('tab_our_proposers_li'),

        defaultCompanyList:'/media/i/default_company_list.png',

        initialize:function () {
            var i, optionsData = this.options.tabContent;
            this.own = optionsData.own;
            for (i in optionsData.sentAcceptedList) {
                if (optionsData.sentAcceptedList.hasOwnProperty(i)) {
                    this.sentAcceptedList.push($.extend(true, {}, optionsData.sentAcceptedList[i]));
                }
            }

            this.initLayout();
        },

        initLayout:function(){
            var i, model, htmlParts=[], liParts=[], item;

            this.$el.empty();
            if (this.sentAcceptedList.length) {
                if(this.own) {
                    htmlParts.push('<h4>Нас рекомендуют: ');
                } else {
                    htmlParts.push('<h4>Данную компанию рекомендуют: ');
                }
                htmlParts.push(this.sentAcceptedList.length);
                htmlParts.push(' ');
                htmlParts.push(Y.utils.morph('компания', this.sentAcceptedList.length, 'i'));
                htmlParts.push('</h4>');

                for (i in this.sentAcceptedList) {
                    if (this.sentAcceptedList.hasOwnProperty(i)) {
                        item = this.sentAcceptedList[i];
                        model = {
                            bname : item.brand_name || '',
                            company_url : '/' + item.rek_id + '/profile/',
                            logo : item.logo || this.defaultCompanyList,
                            kind_of_activity : item.kind_of_activity || ''
                        };

                        liParts.push(this.template_li(model));
                    }
                }

                htmlParts.push(this.template_ul({'content':liParts.join('')}));

                $('#our_proposers').on('click', 'td a', this, function(eventObject) {
                    var url = eventObject.currentTarget.pathname + eventObject.currentTarget.search;
                    Y.ApplicationRouter.navigate(url, {trigger:true});
                    return false;
                });
            } else {
                if(this.own) {
                    htmlParts.push('<h4>Ни одна компания пока не дала нам свою рекомендацию</h4>');
                } else {
                    htmlParts.push('<h4>У данной компании пока нет рекомендаций</h4>');
                }
            }

            this.$el.append(htmlParts.join(''));
        },

        // newData must contain:
        // el,
        // tabContent : {
        //                  sentAcceptedList : [{brand_name, rek_id, logo, kind_of_activity}]
        // }
        setData:function (newData) {
                var i, optionsData = newData.tabContent;

            this.el = newData.el;
            this.$el = $(this.el);

            this.sentAcceptedList = [];

            for (i in optionsData.sentAcceptedList) {
                if (optionsData.sentAcceptedList.hasOwnProperty(i)) {
                    this.sentAcceptedList.push($.extend(true, {}, optionsData.sentAcceptedList[i]));
                }
            }

            this.initLayout();
        }
    });
}
