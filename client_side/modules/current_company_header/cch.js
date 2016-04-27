function x(Y) {
    "use strict";

    Y.CurrentCompanyHeader = Backbone.View.extend({

        events : {
            "click div.verification-set a.settings" : "onClickSettings"
        },

        model : null,

        template : Y.TemplateStore.load('cch_content'),
        locales : Y.Locales['cch'],

        initialize : function() {
            var weGaveRecommend, theyGaveRecommend;
            this.model = {};
            $.extend(this.model, this.options.data);

            if(!this.model.own && this.model.authorized) {
                weGaveRecommend = this.options.data.hasOwnProperty('their_rec_request_status') &&
                    (typeof(this.options.data.their_rec_request_status) !== 1);
                theyGaveRecommend = this.options.data.hasOwnProperty('my_rec_request_status') &&
                    (this.options.data.my_rec_request_status !== 'undefined');
                $.extend(this.model, {
                    my_action_recommend : this.getOurRecommendUrl(weGaveRecommend, this.options.data.verified, this.options.data.rekid),
                    my_title_recommend : this.getOurRecommendTitle(weGaveRecommend, this.options.data.verified),
                    my_text_recommend : this.getOurRecommendText(weGaveRecommend, this.options.data.verified),
                    have_others_recommend : theyGaveRecommend,
                    our_recommend : weGaveRecommend
                });
            }

            this.model.locales = this.locales;
            _.extend(this.model, {
                brandNameCut : Y.utils.cutLongString(this.model.brandName, 32),
                categoryTextCut : Y.utils.cutLongString(this.model.categoryText, 50)
            });
        },

        render : function() {
            this.$el.html(this.template(this.model));
            this.bindEvents();
            return this;
        },

        bindEvents : function() {
            var that = this;
            if(!this.model.own) {
                this.$el.find('#cch-recommend-our').click(function(e) {
                    e.preventDefault();
                    that.onClickOurRecommendAction(e.currentTarget.pathname);
                    return false;
                });
                if(!this.model.have_others_recommend) {
                    this.$el.find('#cch-recommend-their').click(function(e) {
                        e.preventDefault();
                        that.onClickTheirRecommendAction();
                        return false;
                    });
                }
            }
        },

        getOurRecommendUrl : function(isGiven, isVerified, rekId) {
            return isVerified ? (isGiven ? '/recommendations/take-away/' + rekId + '/' :
                '/recommendations/give/' + rekId + '/') : '/';
        },

        getOurRecommendTitle : function(isGiven, isVerified) {
            return isVerified ? (isGiven ? "Отозвать рекомендацию компании" :
                "Дать компании рекомендацию") : "Верифицируйтесь, чтобы дать рекомендацию";
        },

        getOurRecommendText : function(isGiven, isVerified) {
            return isGiven ? "Отозвать рекомендацию" : "Дать рекомендацию";
        },

        onClickOurRecommendAction : function(url) {
            var that = this;
            if(!this.model.verified) {
                Y.VerifiedOnlyMessage(this.locales.verified_only, false);
            } else {
                $.ajax(url, {
                    success : function(data) {
                        if(data.error) {
                            Y.Informer.show(that.model.our_recommend ?
                                                "Ошибка выдачи рекомендации. Попробуйте позже" :
                                                "Ошибка отзыва рекомендации. Попробуйте позже.", 10);
                        } else {
                            that.model.our_recommend = !that.model.our_recommend;
                            that.$el.find('#cch-recommend-our')
                                .attr('href', that.getOurRecommendUrl(that.model.our_recommend, that.model.rekid))
                                .attr('title', (that.model.our_recommend ? "Отозвать рекомендацию компании" : "Дать компании рекомендацию"));
                            that.$el.find('#cch-recommend-our').empty().append(that.model.our_recommend ? "Отозвать рекомендацию" : "Дать рекомендацию");
                        }
                    },
                    error : function(jqXHR, textStatus, errorThrown) {
                        Y.Informer.show(that.model.our_recommend ?
                                            "Ошибка выдачи рекомендации. Попробуйте позже" :
                                            "Ошибка отзыва рекомендации. Попробуйте позже.", 10);
                    },
                    type : 'POST',
                    dataType : 'json',
                    data : { rek_id : that.model.rekid },
                    beforeSend:function (jqXHR) {
                        jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                    }
                });
            }
        },

        onClickTheirRecommendAction : function() {
            var that = this, dialogAskRecommend;
            function onAskRecommendSuccess(data) {
                var result = false;
                if(data.error) {
                    if(data.hasOwnProperty('max_reached')) {
                        Y.Informer.show("Сегодня вы больше не можете запрашивать рекомендации", 10);
                    } else if(data.hasOwnProperty('not_verified')) {
                        Y.Informer.show("Запрашивать рекомендацию можно только у верифицированной компании", 10);
                    } else if(data.hasOwnProperty('unauthorized')) {
                        Y.Informer.show("Вы не авторизованы", 10);
                    } else {
                        Y.Informer.show("Ошибка запроса рекомендации. Попробуйте позже.", 10);
                    }
                } else {
                    that.$el.find('#cch-recommend-their').hide();
                    result = true;
                }
                return result;
            }
            function onAskRecommendError(jqXHR, textStatus, errorThrown) {
                Y.Informer.show("Ошибка запроса рекомендации. Попробуйте позже.", 10);
                return false;
            }

            dialogAskRecommend = new Y.AskRecommendationsDialog({
                url : '/recommendations/ask/' + this.model.rekid + '/',
                rek_id : this.model.rekid,
                success : onAskRecommendSuccess,
                error : onAskRecommendError
            });

            dialogAskRecommend.show();
        },

        onClickSettings : function(e) {
		    Y.ApplicationRouter.navigate('settings/', {trigger : true});
            return false;
        }
    });
}