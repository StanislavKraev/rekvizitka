function x(Y) {
    "use strict";

    Y.TabIncomingRequests = Backbone.View.extend({
        template : Y.TemplateStore.load('tab_in_reqs_content'),
        container : null,
        content : null,
        locale : Y.Locales['tab_in_reqs'],

        inreqCurrentPage : 1,
        pageElements : null,
        inreqElementMap : null,
        inreqItemsPerPage : 5,
        inreqPageSpan : 10,

        initialize : function() {
            this.content = this.options.tabContent;
            this.container = this.options.container;
            this.el = this.options.el;
            this.$el = $(this.el);
            this.initLayout();
        },

        getHeadLine : function() {
            var inReqNumber = this.content.incoming_requests.length,
                isPlural = this.isPluralLinguisticForm(inReqNumber);
            return (inReqNumber === 0 ? this.locale.no_incoming_requests :
                (isPlural ? this.locale.you_have_many : this.locale.you_have_one) + ' ' +
                    inReqNumber + ' ' +
                    Y.utils.morph(this.locale.requests_single, inReqNumber, 'i'));
        },

        isPluralLinguisticForm : function(num) {
            var numRest = num % 100;
            if(numRest > 1 && numRest < 21) {
                return true;
            }
            return numRest % 10 !== 1;
        },

        initLayout : function() {
            var initData = {
                headline : this.getHeadLine()
            };

            this.$el.empty().append(this.template(initData));

            if(this.content.incoming_requests.length > 0) {
                this.inreqCurrentPage = Y.utils.getURLparam('p', 'number') || 1;
                this.$el.find('#incominglist ul').show();
                this.drawListElements();
                this.bindUserEvents();
            } else {
                this.$el.find('#inominglist ul').hide();
            }
            this.doPagination(this.getPageCount(), this.inreqCurrentPage);
        },

        setData : function(params) {
            this.content = params.tabContent;
            this.initLayout();
        },

        getPageCount : function() {
            return Math.ceil(this.content.incoming_requests.length / this.inreqItemsPerPage);
        },

        getRange : function() {
            var inReqList = this.content.incoming_requests;
            return inReqList.slice(this.inreqItemsPerPage * (this.inreqCurrentPage-1),
                this.inreqItemsPerPage * this.inreqCurrentPage);
        },

        drawListElements : function() {
            var inreqItem, inrekId, that = this;

            this.pageElements = [];
            this.inreqElementMap = {};

            $(document).scroll(function() {
                that.bindScroll();
            });

            $.each(this.getRange(), function(iterId, iterItem) {
                inrekId = iterItem.get('rek_id');
                $('ul.incomingpage').append('<li id="listelem_' + inrekId + '"></li>');
                inreqItem = new Y.IncomingRequestListItemView({
                    el:$('#listelem_' + inrekId),
                    model:iterItem,
                    tab : that,
                    container:that.container
                });
                inreqItem.show();
                that.pageElements.push(inreqItem);
                that.inreqElementMap[inrekId] = inreqItem;
            });

            this.bindScroll();
        },

        bindUserEvents : function() {
            var that = this;
            this.$el.find('ul.incomingpage').on('click', 'a.accept-req', function (e) {
                var partnerRekId = e.currentTarget.id.split('_')[1];
                e.preventDefault();
                that.acceptIncomingRequest(partnerRekId);
                return false;
            });

            this.$el.find('ul.incomingpage').on('click', 'a.cancel-req', function(e) {
                var partnerRekId = e.currentTarget.id.split('_')[1];
                e.preventDefault();
                that.declineIncomingRequest(partnerRekId);
                return false;
            });
        },

        bindScroll : function() {
            var pageBottom = $(document).scrollTop() + $(window).height();
            this.trigger('scrollToView', { pageBottom : pageBottom });
        },

        acceptIncomingRequest : function(rekId) {
            var that = this;
            $.ajax('/contractors/accept/', {
                success : function(data) {
                    var accElem;
                    if(data.error) {
                        Y.Informer.show("Невозможно добавить компанию в контрагенты. Попробуйте позже.", 10);
                    } else {
                        if(that.container.model.moveRecordFromIncomingToMain(rekId)) {
                            accElem = that.$el.find("#listelem_" + rekId);
                            accElem.find('.hover-box .button').hide();
                            accElem.find('.block-accept-msg').show();
                        } else {
                            Y.Informer.show("Ошибка переноса заявки в список контрагентов", 10);
                        }
                    }
                },
                error : function(jqXHR, textStatus, errorThrown) {
                    Y.Informer.show("Невозможно добавить компанию в контрагенты, попробуйте позже.", 10);
                },
                type : 'POST',
                dataType : 'json',
                data : { rek_id : rekId },
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        declineIncomingRequest : function(rekId) {
            var that = this;

            function onDeclineIncomingSuccess(data) {
                var delElem;
                if(data.error) {
                    Y.Informer.show("Невозможно отклонить заявку. Попробуйте позже.", 10);
                } else {
                    if(that.container.model.deleteFromArray(rekId, 'incoming_requests')) {
                        delElem = that.$el.find("#listelem_" + rekId);
                        delElem.find('.hover-box .button').hide();
                        delElem.find('.block-revive').show();
                        delElem.find('.block-revive a').click(function(e) {
                            e.preventDefault();
                            that.confirmRevivingDeclinedRequest(rekId);
                            return false;
                        });
                    } else {
                        Y.Informer.show("Невозможно отклонить заявку, попробуйте позже.", 10);
                    }
                }
            }

            $.ajax('/contractors/reject/', {
                success : onDeclineIncomingSuccess,
                error : function(jaXHR, textStatus, errorThrown) {
                    Y.Informer.show("Невозможно отклонить заявку, попробуйте позже.", 10);
                },
                data : { rek_id : rekId },
                type : 'POST',
                dataType : 'json',
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        confirmRevivingDeclinedRequest : function(rekId) {
            var that = this;
            Y.Modalbox.showSimple("Вы действительно хотите вернуть отклоненную заявку?",
                [
                    {
                        bcaption : "Вернуть",
                        bstyle : "action",
                        callback : function() {
                            that.reviveDeclinedRequest(rekId);
                        }
                },
                    {
                        bcaption : "Отмена",
                        bstyle : 'simple'
                    }
                ], 360);
        },

        reviveDeclinedRequest : function(rekId) {
            var that = this;
            $.ajax('/contractors/add/', {  // todo: the URL will change soom
                success : function(data) {
                    var delElem;
                    if(data.error) {
                        Y.Informer.show("Невозможно восстановить заявку. Попробуйте позже.", 10);
                    } else {
                        if(that.container.model.reviveFromCancelled(rekId, 'incoming_requests')) {
                            delElem = that.$el.find("#listelem_" + rekId);
                            delElem.find('.hover-box .button').show();
                            delElem.find('.block-revive').hide();
                        } else {
                            Y.Informer.show("Ошибка восстановления заявки на клиенте", 10);
                        }
                    }
                },
                error : function(jqXHR, textStatus, errorThrown) {
                    Y.Informer.show("Невозможно восстановить заявку, попробуйте позже.", 10);
                },
                data : { rek_id : rekId },
                type : 'POST',
                dataType : 'json',
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        doPagination : function(pageCount, currentPage) {
            if(pageCount > 1) {
                if(!this.paginator) {
                    this.paginator = new Y.Paginator({
                        paginatorHolder : "paginator1", // id контейнера, куда ляжет пагинатор
                        pagesSpan : this.inreqPageSpan, // число страниц, видимых одновременно
                        baseUrl : function(i) {
                            return '/contractors/incoming/?p=' + i;
                        },
                        el : this.$el.find('.incoming-pagination')
                    });
                }

                this.paginator.render(pageCount, currentPage);
                this.paginator.bindChangePageEvent(this.onPageChanged, this);
            } else {
                this.$el.find('.incoming-pagination').empty();
                this.paginator = null;
            }
        },

        onPageChanged : function(pageId, url) {
            Y.ApplicationRouter.navigate(url, { trigger : true });
        }
    });

    Y.IncomingRequestListItemView = Backbone.View.extend({
        container : null,
        template : Y.TemplateStore.load('tab_in_reqs_listitem'),
        locale : Y.Locales['tab_in_reqs'],
        tab : null,

        initialize : function() {
            this.container = this.options.container;
            this.el = this.options.el;
            this.tab = this.options.tab;
            this.$el = $(this.el);
        },

        show : function() {
            var that = this,
                itemdata = {
                company_url : '/' + this.model.get('rek_id') + '/profile/',
                bname : this.model.get('brand_name'),
                bnamecut : Y.utils.cutLongString(this.model.get('brand_name'), 30),
                logo : this.model.get('logo'),
                kind_of_activity : this.model.get('kind_of_activity'),
                rek_id : this.model.get('rek_id')
            };
            this.$el.empty();
            this.$el.append(this.template(itemdata));
            this.$el.find('.block-revive').hide();
            this.$el.find('.block-accept-msg').hide();

            if(!this.model.get('viewed')) {
                this.personalScroll = function(params) {
                    return that.onScrollContainer(params);
                };
                this.tab.bind('scrollToView', this.personalScroll, this);
            }
        },

        onScrollContainer : function(params) {
            var elTop = this.$el.position().top;

            if(params.pageBottom > elTop) {
                this.container.markAsViewed(this.model.get('rek_id'));
                this.tab.unbind('scrollToView', this.personalScroll);
            }
        }
    });
}
