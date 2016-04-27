function x(Y) {
    "use strict";

    Y.TabOutgoingRequests = Backbone.View.extend({
        template : Y.TemplateStore.load('tab_out_reqs_content'),
        container : null,
        content : null,
        locale : Y.Locales['tab_out_reqs'],

        outreqCurrentPage : 1,
        pageElements : null,
        outreqElementMap : null,
        outreqItemsPerPage : 5,
        outreqPageSpan : 10,

        initialize : function() {
            this.content = this.options.tabContent;
            this.container = this.options.container;
            this.el = this.options.el;
            this.$el = $(this.el);
            this.initLayout();
        },

        getHeadLine : function() {
            var outReqNumber = this.content.outgoing_requests.length;
            return (outReqNumber === 0 ? this.locale.no_outgoing_requests :
                      this.locale.you_made + ' ' + outReqNumber + ' ' +
                Y.utils.morph(this.locale.requestsNumber, outReqNumber, 'v'));
        },

        initLayout : function() {
            var initData = {
                headline : this.getHeadLine()
            };

            this.$el.empty().append(this.template(initData));

            if(this.content.outgoing_requests.length > 0) {
                this.outreqCurrentPage = Y.utils.getURLparam('p', 'number') || 1;
                this.$el.find('#outgoinglist ul').show();
                this.drawListElements();
                this.bindUserEvents();
            } else {
                this.$el.find('#outgoinglist ul').hide();
            }
            this.doPagination(this.getPageCount(), this.outreqCurrentPage);
        },

        setData : function(params) {
            this.content = params.tabContent;
            this.initLayout();
        },

        getPageCount : function() {
            return Math.ceil(this.content.outgoing_requests.length / this.outreqItemsPerPage);
        },

        getRange : function() {
            var outReqList = this.content.outgoing_requests;
            return outReqList.slice(this.outreqItemsPerPage * (this.outreqCurrentPage-1),
                this.outreqItemsPerPage * this.outreqCurrentPage);
        },

        drawListElements : function() {
            var outreqItem, dialogId, that = this;

            this.pageElements = [];
            this.outreqElementMap = {};

            $.each(this.getRange(), function(iterId, iterItem) {
                dialogId = iterItem.get('rek_id');
                $('ul.outgoingpage').append('<li id="listelem_' + dialogId + '"></li>');
                outreqItem = new Y.OutgoingRequestListItemView({
                    el:$('#listelem_' + dialogId),
                    model:iterItem,
                    container:that.container
                });
                outreqItem.show();
                that.pageElements.push(outreqItem);
                that.outreqElementMap[dialogId] = outreqItem;
            });
        },

        bindUserEvents : function() {
            var that = this;
            this.$el.find('ul.outgoingpage').on('click', 'a.write-a-message', function (e) {
                var corrId = e.currentTarget.id.split('_')[1];
                e.preventDefault();
                that.openDialog(corrId);
                return false;
            });

            this.$el.find('ul.outgoingpage').on('click', 'a.cancel-req', function(e) {
                var partnerRekId = e.currentTarget.id.split('_')[1];
                e.preventDefault();
                that.cancelOutgoingRequest(partnerRekId);
                return false;
            });
        },

        openDialog : function(corrId) {
            Y.ApplicationRouter.navigate('/chat/start_dialog/' + corrId + '/', { replace : false, trigger : true });
        },

        cancelOutgoingRequest : function(rekId) {
            var that = this;

            function onCancelOutgoingSuccess(data) {
                var delElem;
                if(data.error) {
                    Y.Informer.show("Невозможно отменить заявку. Попробуйте позже.", 10);
                } else {
                    if(that.container.model.deleteFromArray(rekId, 'outgoing_requests')) {
                        delElem = that.$el.find("#listelem_" + rekId);
                        delElem.find('.hover-box .button').hide();
                        delElem.find('.block-cancel-msg').show();
                    } else {
                        Y.Informer.show("Ошибка отмены заявки на клиенте", 10);
                    }
                }
            }

            $.ajax('/contractors/delete/', {
                success : onCancelOutgoingSuccess,
                error : function(jqXHR, textStatus, errorThrown) {
                    Y.Informer.show("Невозможно отменить заявку, попробуйте позже.", 10);
                },
                type : 'POST',
                data : { rek_id : rekId },
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
                        pagesSpan : this.outreqPageSpan, // число страниц, видимых одновременно
                        baseUrl : function(i) {
                            return '/contractors/outgoing/?p=' + i;
                        },
                        el : this.$el.find('.outgoing-pagination')
                    });
                }

                this.paginator.render(pageCount, currentPage);
                this.paginator.bindChangePageEvent(this.onPageChanged, this);
            } else {
                this.$el.find('.outgoing-pagination').empty();
                this.paginator = null;
            }
        },

        onPageChanged : function(pageId, url) {
            Y.ApplicationRouter.navigate(url, { trigger : true });
        }
    });

    Y.OutgoingRequestListItemView = Backbone.View.extend({
        container : null,
        template : Y.TemplateStore.load('tab_out_reqs_listitem'),
        locale : Y.Locales['tab_out_reqs'],

        initialize : function() {
            this.container = this.options.container;
            this.el = this.options.el;
            this.$el = $(this.el);
        },

        show : function() {
            var itemdata = {
                company_url : '/' + this.model.get('rek_id') + '/profile/',
                bname : this.model.get('brand_name'),
                bnamecut : Y.utils.cutLongString(this.model.get('brand_name'), 30),
                logo : this.model.get('logo'),
                kind_of_activity : this.model.get('kind_of_activity'),
                rek_id : this.model.get('rek_id'),
                corr_id : this.model.get('employee_id')
            };
            this.$el.empty();
            this.$el.append(this.template(itemdata));
            this.$el.find('.block-cancel-msg').hide();
        }
    });
}
