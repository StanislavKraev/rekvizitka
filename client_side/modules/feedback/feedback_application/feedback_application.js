function x(Y) {
    "use strict";

    var FeedbackApplicationView;

    FeedbackApplicationView = Y.GeneralPortlet.extend({
        locales:Y.Locales['feedback_application'],
        LG:Y.localesGlobal,
        template:Y.TemplateStore.load('feedback_application_content'),

        values: null,

        portletDataProperty : 'Feedback_init',
        portletDataLoadURL : '/feedback/i/',

        /* overrides from GeneralPortlet */

        getLoadPortletDataURL : function() {
            return this.portletDataLoadURL;
        },

        childLoadPortletDataSuccess : function() {
            // Y[this.portletDataProperty] = this.ajaxResponse.data;
            if(this.ajaxResponse.data.error) {
                Y.Informer.show("Ошибка инициализации обратной связи на сервере: " + this.ajaxResponse.data.error, 10);
            } else {
                Y[this.portletDataProperty] = this.ajaxResponse.data;
            }
        },

        childLoadPortletDataError : function() {
            Y.Informer.show("Ошибка инициализации обратной связи: " + this.ajaxError.errorThrown, 30);
        },

        childProcessPortletData : function() {
            if(Y[this.portletDataProperty].hasOwnProperty('email')) {
                this.values = { email : Y[this.portletDataProperty].email };
            } else {
                this.values = { email : '' };
            }
        },

        childInitializePortlet : function() {
            return true;
        },

        childPageInstanceActivated : function() {
            return true;
        },

        getClassModuleName : function() {
        },

        childPrepareDrawPortlet : function() {
            var value = {}, html;
            $.extend(value, this.locales, {
                send : this.LG.buttons.send || '',
                email : this.values.email || ''
            });
            html = this.template(value);
            this.$el.append(html);
            $('a.send', this.$el).click({ 'that' : this }, this.doSend);
            return false;
        },

        childUpdatePageInstance : function() {
        },

        childUpdateSidebar : function() {
            this.options.mainSidebar.setMode('feedback', {});
        },

        childOpenPageTab : function() {
        },
        /* overrides end */

        checkValue : function (element, type) {
            var value = $(element).val(),
                that = this;

            switch (type) {
                case 'email':
                    if (!Y.utils.isEmail(value)) {
                        $(element).addClass('error')
                            .after('<div class="error">' + that.LG.messages.wrong.email + '</div>');
                        value = false;
                    }
                    break;
                case 'text':
                    if (value === '') {
                        $(element).addClass('error')
                            .after('<div class="error">' + that.LG.messages.error.empty + '</div>');
                        value = false;
                    }
                    break;
            }

            return value;
        },

        doAjax : function (data) {
            var that = this;

            function onSendAjaxSuccess(data) {
                if (data.error) {
                    Y.Informer.show(that.LG.messages.error.server, 10);
                } else {
                    Y.Modalbox.showSimple(that.LG.messages.good.sending);
                    $('#feedback #feedback-message').val('');
                }
            }

            $.ajax('/feedback/', {
                success:onSendAjaxSuccess,
                error:function () {
                    Y.Informer.show(that.LG.messages.wrong.sending, 10);
                },
                type:'POST',
                data:data,
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        processData : function () {
            var data = {}, i;

            $('div.error').remove();
            $('.error').removeClass('error');

            data.msg = this.checkValue('#feedback #feedback-message', 'text');
            data.email = this.checkValue('#feedback #feedback-email', 'email');

            for(i in data) {
                if(data.hasOwnProperty(i)) {
                    if(!data[i]) {
                        data = false;
                        break;
                    }
                }
            }

            if (data) {
                data.extra_field = Y.utils.getCookie('csrftoken');
                this.doAjax(data);
            }
        },

        doSend:function (e) {
            var that = e.data.that;
            that.processData();
            return false;
        }

        /*
        activate:function (options) {
            var html, value = {},
                thisView = this;

            options.deactivatePrevious();

            this.options.mainSidebar.setMode('feedback', {});
            $.extend(value, this.locales, {
                send:this.LG.buttons.send || '',
                email:this.values.email || ''
            });
            html = this.template(value);
            this.$el.append(html);
            $('a.send', this.$el).click({'thisView':thisView}, thisView.doSend);
        },

        deactivate:function () {
            this.preparedUi = this.$el.children().detach();
        },

        initialize:function () {
            var that = this;
            this.values = {};
            if(Y.Feedback_init) {
                this.values = Y.Feedback_init;
            } else {
                $.ajax('/feedback/i/', {
                    success: function(data) {
                        if(data.error) {
                            Y.Informer.show("Ошибка инициализации обратной связи: " + data.error, 10);
                        } else {
                            if(data.hasOwnProperty('email')) {
                                that.values = { email : data.email };
                                $("#feedback-email").val(data.email);
                            } else {
                                that.values = { email : '' };
                            }
                        }
                    },
                    error:function () {
                        Y.Informer.show(that.LG.messages.wrong.sending, 3);
                    },
                    type:'GET',
                    data: {},
                    dataType:'json',
                    beforeSend:function (jqXHR) {
                        jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                    }
                });
            }
        }*/
    });

    Y.FeedbackApplication = FeedbackApplicationView;
}
