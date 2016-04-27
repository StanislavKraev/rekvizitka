function x(Y) {
    "use strict";
    Y.ProfileAboutView = Backbone.View.extend({
        linkProfileAplication:{},
        tabContent:{},
        template:Y.TemplateStore.load('profile_about_view_content'),
        template_edit:Y.TemplateStore.load('profile_about_view_content_edit'),

        initialize:function () {
            this.initLayout();
        },

        startEdit:function (e) {
            var thisView = e.data.thisView;

            thisView.tabContent.descrHTML = thisView.tabContent.descr;

            thisView.$el.empty().append(thisView.template_edit(thisView.tabContent));

//            thisView.$el.find('#descr').elastic();

            thisView.$el.find('select').selectBox();

            return false;
        },

        startSave:function (e) {
            var that = e.data.thisView,
                linkProfileAplication = e.data.thisView.options.thisProfileApplication,

                data = JSON.stringify({
                    brandName:$('#brandName').val(),
                    descr:$('#descr').val(),
                    descrHTML:Y.utils.wrapEachLine(Y.utils.escapeStr($('#descr').val()), '', '<br>'),
                    shortName:$('#shortName').val(),
                    fullName:$('#fullName').val(),
                    categoryText:$('#categoryText').val(),
                    genDir:$('#genDir').val(),
                    genAcc:$('#genAcc').val(),
                    estYear:$('#estYear').val(),
                    staffSize:$('#staffSize').val(),
                    inn:$('#inn').val(),
                    kpp:$('#kpp').val(),
                    bank_account:{
                        bank:$('#bank_account-bank').val(),
                        bank_address:$('#bank_account-bank_address').val(),
                        bik:$('#bank_account-bik').val(),
                        correspondent_account:$('#bank_account-correspondent_account').val(),
                        settlement_account:$('#bank_account-settlement_account').val(),
                        recipient:$('#bank_account-recipient').val()
                    },
                    categories : that.getCompanyCategories()
                });

            linkProfileAplication.moduleProcessAbout(data, e.data.thisView);

            return false;
        },

        getCompanyCategories : function() {
            var cats = [];
            $('.company_categories:checked').map(function() {
                cats.push(this.name);
            });
            return cats;
        },

        cancelEdit:function (e) {
            var thisView = e.data.thisView;
            thisView.$el.empty().append(thisView.template(thisView.tabContent));

            return false;
        },

        initLayout:function () {
            var tab = this.options.thisProfileApplication.appSettings,
                categoryElements = [];

            $.each(tab.profile.information.categories, function(id, itCategory) {
                categoryElements.push({
                    name : itCategory.id,
                    title : itCategory.repr,
                    val: itCategory.state
                });
            });

            this.tabContent = $.extend(
                tab.profile.information,
                tab.profile.essential_elements,
                {
                    descrHTML:Y.utils.wrapEachLine(Y.utils.escapeStr(tab.profile.descr || ''), '', '<br>'),
                    descr:tab.profile.descr,

                    authorized:tab.authorized,
                    rek_id:tab.rek_id,
                    verified:tab.verified,
                    own_company:tab.own_company,
                    company_logo:tab.company_logo,

                    staff_size_select : tab.staff_size_select || [[0, 'Не задано'],0],
                    staff_size_select_current : 0,
                    staffSize : tab.staffSize || 0,

                    categoryElements : categoryElements
                }
            );

            this.$el.append(this.template(this.tabContent));

            $('#profile').on('click', 'a.edit', {'thisView':this}, this.startEdit);
            $('#profile').on('click', 'a.save', {'thisView':this}, this.startSave);
            $('#profile').on('click', 'a.cancel', {'thisView':this}, this.cancelEdit);
            $('#profile').on('click', 'a.ccat_view', this, this.navigateSearch);
        },

        navigateSearch : function(eventObject) {
            var url = eventObject.currentTarget.pathname + eventObject.currentTarget.search;
            Y.ApplicationRouter.navigate(url, {trigger:true});
            return false;
        },

        reinitLayout:function () {
            this.$el.empty();
            this.initLayout();
        },

        setData:function (newData) {
            this.$el = newData.el || this.$el;
            this.el = this.$el[0];
            this.reinitLayout();
        }
    });
}