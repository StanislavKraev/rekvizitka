function x(Y) {
    "use strict";

    Y.TabPartnersList = Backbone.View.extend({
        template : Y.TemplateStore.load('tab_partners_list_content'),
        settingsDialogTemplate : Y.TemplateStore.load('tab_partners_list_editsettings'),
        locale : Y.Locales['tab_partners_list'],
        container : null,
        content : null,

        pageElements : null,
        partnerElementMap : null,
        partnerItemsPerPage : 5,
        partnerCurrentPage : 1,
        partnerPagesSpan : 10,

        initialize : function() {
            this.content = this.options.tabContent;
            this.container = this.options.container;
            this.el = this.options.el;
            this.$el = $(this.el);
            this.initLayout();
        },

        getQueryParam : function() {
            return Y.utils.getURLparam('q') || '';
        },

        getHeadLine : function() {
            var query = this.getQueryParam(),
                lineStart = (this.container.own ? this.locale.you_have : this.locale.company_has);
            return (query === '' ? lineStart : this.locale.ptnrs_found) + ' ' +
                    (this.content.rek_partners.length > 0 ?
                        String(this.content.rek_partners.length) + ' ' +
                        Y.utils.morph(this.locale.partnersNumber, this.content.rek_partners.length, 'i') :
                        "нет контрагентов");
        },

        initLayout : function() {
            var that = this, headLine, ptnrsQuery;

            ptnrsQuery = this.getQueryParam();
            headLine = this.getHeadLine();

            this.$el.empty().append(this.template({
                headline : headLine,
                search_ptnrs_placeholder : this.locale.search_placeholder,
                query_value : ptnrsQuery,
                query_input_style : (ptnrsQuery === '' ? 'noquery' : 'query')
            }));

            if(this.content.rek_partners.length > 0) {
                this.partnerCurrentPage = Y.utils.getURLparam('p', 'number') || 1;

                this.drawListElements();

                this.$el.find('ul.partnerspage').on('click', 'a.write-a-message', function (e) {
                    var corrId = e.currentTarget.id.split('_')[1];
                    e.preventDefault();
                    that.openPartnerDialog(corrId);
                    return false;
                });

                this.$el.find('ul.partnerspage').on('click', 'a.partner-edit', function(e) {
                    var partnerRekId = e.currentTarget.id.split('_')[1];
                    e.preventDefault();
                    that.editPartnerSettings(partnerRekId);
                    return false;
                });
            }
            this.doPagination(this.getPageCount(), this.partnerCurrentPage);
        },

        setData : function(params) {
            this.content = params.tabContent;
            this.container = params.container;
            this.el = params.el;
            this.$el = $(this.el);
            this.initLayout();
        },

        openPartnerDialog : function(corrId) {
            Y.ApplicationRouter.navigate('/chat/start_dialog/' + corrId + '/', { replace : false, trigger : true });
        },

        editPartnerSettings : function(rekId) {
            var partnerElem = this.container.model.getElementByRekId(rekId, 'rek_partners'),
                formSettingsNames = {
                    privacy : "select#view-mode"
                },
                that = this,
                currentValues = {};

            function onSavePartnerSettingsSuccess(data) {
                var i;
                if(data.error) {
                    Y.Informer.show("Невозможно сохранить настройки контрагента. Попробуйте позже.", 10);
                } else {
                    for(i in currentValues) {
                        if(currentValues.hasOwnProperty(i)) {
                            if(i !== 'rek_id') {
                                partnerElem.set(i, currentValues[i]);
                            }
                        }
                    }
                    that.container.model.set('needReload', true);
                    Y.Informer.show("Настройки успешно сохранены", 10);
                }
            }

            function onSaveSettingsButtonClick(valuesMap) {
                var i;
                for(i in formSettingsNames) {
                    if(formSettingsNames.hasOwnProperty(i)) {
                        currentValues[i] = valuesMap[formSettingsNames[i]];
                    }
                }
                currentValues.rek_id = rekId;
                $.ajax('/contractors/settings/', {
                    success : onSavePartnerSettingsSuccess,
                    error : function(jqXHR, textStatus, errorThrown) {
                        Y.Informer.show("Невозможно сохранить настройки контрагента, попробуйте позже.", 10);
                    },
                    type : 'POST',
                    dataType : 'json',
                    data : currentValues,
                    beforeSend : function (jqXHR) {
                        jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                    }
                });
            }

            Y.Modalbox.showCustom({
                buttons : [
                    {
                        bcaption : 'Сохранить',
                        bstyle : 'action',
                        callback : onSaveSettingsButtonClick
                    },
                    {
                        bcaption : 'Отмена',
                        bstyle : 'simple'
                    }
                ],
                template : this.settingsDialogTemplate,
                width : 458,
                inputNames : [ formSettingsNames.privacy ],
                templateParams : {
                    view_mode : partnerElem.get('privacy'),
                    content_align_class: 'text-left',
                    rek_id : rekId,
                    brand_name : partnerElem.get('brand_name'),
                    brand_name_cut : Y.utils.cutLongString(partnerElem.get('brand_name'), 30)
                },
                customInitTemplate : function() {
                    var thatbox = this;
                    this.getModalNode().find('select').selectBox();

                    this.getModalNode().find('a.remove-from-partners').click(function(e) {
                        e.preventDefault();
                        Y.Modalbox.showSimple('Вы действительно хотите удалить компанию "' + partnerElem.get('brand_name') +
                            '" из ваших контрагентов?', [
                            {
                                bcaption : "Удалить",
                                bstyle : 'action',
                                callback : function() {
                                    Y.Modalbox.removeBox(thatbox.getId());
                                    that.deletePartnerFromList(rekId);
                                }
                            },
                            {
                                bcaption : "Отмена",
                                bstyle : 'simple'
                            }
                        ], 360);
                        return false;
                    });
                }
            });
        },

        deletePartnerFromList : function(rekId) {
            var that = this;

            function onDeletePartnerSuccess(data) {
                if(data.error) {
                    Y.Informer.show("Невозможно удалить контрагента. Попробуйте позже.", 10);
                } else {
                    if(that.container.model.deleteFromArray(rekId, 'rek_partners')) {
                        that.initLayout();
                    } else {
                        Y.Informer.show("Ошибка удаления контрагента на клиенте");
                    }
                }
            }

            $.ajax('/contractors/delete/', {
                success : onDeletePartnerSuccess,
                error : function(jqXHR, textStatus, errorThrown) {
                    Y.Informer.show("Невозможно удалить контрагента, попробуйте позже.", 10);
                },
                type : 'POST',
                dataType : 'json',
                data : { rek_id : rekId },
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },

        getPageCount : function() {
            return Math.ceil(this.content.rek_partners.length / this.partnerItemsPerPage);
        },

        getRange : function() {
            var dialist = this.content.rek_partners;
            return dialist.slice(this.partnerItemsPerPage * (this.partnerCurrentPage-1),
                                    this.partnerItemsPerPage * this.partnerCurrentPage);
        },

        drawListElements : function() {
            var partnerItem, ptnrRekId, that = this;

            this.pageElements = [];
            this.dialogIdElementMap = {};

            $.each(this.getRange(), function(iterId, iterItem) {
                ptnrRekId = iterItem.get('rek_id');
                $('ul.partnerspage').append('<li id="listelem_' + ptnrRekId + '"></li>');
                partnerItem = new Y.PartnerListElementView({
                    el:$('#listelem_' + ptnrRekId),
                    model:iterItem,
                    container:that.container,
                    own : that.container.own
                });
                partnerItem.show();
                that.pageElements.push(partnerItem);
                that.dialogIdElementMap[ptnrRekId] = partnerItem;
            });
        },

        doPagination : function(quantity, current) {
            var that = this, query = this.getQueryParam();

            if(quantity > 1) {
                if(!this.paginator) {
                    this.paginator = new Y.Paginator({
                        paginatorHolder : "paginator1", // id контейнера, куда ляжет пагинатор
                        pagesSpan : this.partnerPagesSpan, // число страниц, видимых одновременно
                        baseUrl : function(i) {
                            return '/' + that.content.rek_id + '/contractors/?p=' + i +
                                (query === '' ? '' : '&q=' + query);
                        },
                        el : this.$el.find('.partner-pagination')
                    });
                }

                this.paginator.render(quantity, current);
                this.paginator.bindChangePageEvent(this.onPageChanged, this);
            } else {
                this.$el.find('.partner-pagination').empty();
                this.paginator = null;
            }
        },

        onPageChanged : function(pageId, url) {
            Y.ApplicationRouter.navigate(url, { trigger : true });
        }
    });

    Y.PartnerListElementView = Backbone.View.extend({
        container : null,
        own : false,
        template : Y.TemplateStore.load('tab_partners_list_listelem'),
        locale : Y.Locales['tab_partners_list'],

        initialize : function() {
            this.container = this.options.container;
            this.own = this.options.own;
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
                corr_id : this.model.get('employee_id'),
                rek_id : this.model.get('rek_id'),
                own : this.own
            };
            this.$el.empty();
            this.$el.append(this.template(itemdata));
        }
    });
}
