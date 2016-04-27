function x(Y) {
    "use strict";

    var TabVerification, InvoiceView;

    // options must contain:
    // - billCreated : bool
    // - billData: {id, number, issued, service_title, price}
    // - billStatusMessage
    // - url_print
    // - url_pdf
    InvoiceView = Backbone.View.extend({

        template:Y.TemplateStore.load('tab_verification_invoice'),

        data:{},
        initialize:function () {
            this.data = {
                bill_created:this.options.billCreated,
                number:this.options.billData.number,
                issued:this.options.billData.issued,
                service_title:this.options.billData.service_title,
                price:this.options.billData.price,
                status:this.options.billStatusMessage,
                url_print:this.options.url_print,
                url_pdf:this.options.url_pdf
            };
        },
        render:function () {
            this.$el.html(this.template(this.data));
            return this;
        }
    });

    // options must contain:
    // el
    // tabContent : {
    //                 bill : {id, service_title, price, status, issued, number}
    //                 sentAcceptedList : [{rek_id, brand_name, logo, kind_of_activity}]
    //                 sentNotAcceptedList : [{rek_id, brand_name}]
    //                 verifyRecNumber # todo: start here
    // }

    TabVerification = Backbone.View.extend({
        events:{
            "click a.button.ask-check":"onCreateInvoiceClick",
            "click a.send-bill-to-email":"onSendBillToEmail"
        },

        billStatusMessage:'',
        sentAcceptedList:[],
        sentNotAcceptedList:[],
        canAskRecommendation:false,
        billData:{},
        template:Y.TemplateStore.load('tab_verification_content'),
        template_ul:Y.TemplateStore.load('tab_verification_ul'),
        template_li:Y.TemplateStore.load('tab_verification_li'),
        dialogTemplate:Y.TemplateStore.load('tab_verification_dialog'),
        locales :Y.Locales['tab_verification'],
        initialized:false,
        active:false,
        url_print:'',
        url_pdf:'',

        initialize:function () {
            var optionsData = this.options.tabContent, i;

            for (i in optionsData.sentAcceptedList) {
                if (optionsData.sentAcceptedList.hasOwnProperty(i)) {
                    this.sentAcceptedList.push($.extend({}, optionsData.sentAcceptedList[i]));
                }
            }

            for (i in optionsData.sentNotAcceptedList) {
                if (optionsData.sentNotAcceptedList.hasOwnProperty(i)) {
                    this.sentNotAcceptedList.push($.extend({}, optionsData.sentNotAcceptedList[i]));
                }
            }

            if (optionsData.bill) {
                this.billData = $.extend(true, {}, optionsData.bill);

                this.url_print = '/get/' + this.billData.id + '/bill.html';
                this.url_pdf = '/get/' + this.billData.id + '/bill.pdf';
                this.billCreated = true;

                if (this.billData.status === 0) {
                    this.billStatusMessage = this.locales.statusNotPaid;
                }
            } else {
                this.billCreated = false;
            }

            this.canAskRecommendation = !optionsData.maxRequestCountReached;
            this.verifyRecNumber = optionsData.verifyRecNumber;
            this.initLayout();
        },

        initLayout:function () {
            var i = 1, arr = [], berr = [], item,
                hrefTemplate = _.template('<a href="<%=href%>" title=""><%=content%></a>'),
                sentAcceptedList, sentNotAcceptedList, invoiceView;

            this.$el.empty();

            for (i in this.sentAcceptedList) {
                if (this.sentAcceptedList.hasOwnProperty(i)) {
                    item = this.sentAcceptedList[i];
                    arr.push(hrefTemplate({
                        href:"/" + item.rek_id + "/profile/",
                        content:item.brand_name
                    }));
                }
            }
            sentAcceptedList = arr.join(', ');

            for (i in this.sentNotAcceptedList) {
                if (this.sentNotAcceptedList.hasOwnProperty(i)) {
                    item = this.sentNotAcceptedList[i];
                    berr.push(hrefTemplate({
                        href:'/' + item.rek_id + '/profile/',
                        content:item.brand_name
                    }));
                }
            }
            sentNotAcceptedList = berr.join(', ');

            this.$el.append(this.template({
                sent_not_accepted_list:sentNotAcceptedList,
                sent_accepted_list:sentAcceptedList,
                not_sent:this.sentNotAcceptedList.length + this.sentAcceptedList.length === 0,
                can_ask_recommendation:this.canAskRecommendation,
                verify_rec_number:this.verifyRecNumber,
                vrn_companies:Y.utils.morph('компания', this.verifyRecNumber, 'i'),
                vrn_will_give:Y.utils.morph_verb('давать', this.verifyRecNumber, 'b')
            }));

            invoiceView = new InvoiceView({
                billCreated:this.billCreated,
                billData:this.billData,
                billStatusMessage:this.billStatusMessage,
                url_print:this.url_print,
                url_pdf:this.url_pdf
            });
            this.$el.find('#invoice_view').html(invoiceView.render().el);

            this.$el.find('div.panel-result').on('click', 'td.column1 a, td.column2 a', this, function(eventObject) {
                var url = eventObject.currentTarget.pathname + eventObject.currentTarget.search;
                Y.ApplicationRouter.navigate(url, {trigger:true});
                return false;
            });
        },

        setData:function (newData) {
            var optionsData = newData.tabContent, i;
            this.el = newData.el;
            this.$el = (this.el);

            this.sentAcceptedList = [];
            this.sentNotAcceptedList = [];

            for (i in optionsData.sentAcceptedList) {
                if (optionsData.sentAcceptedList.hasOwnProperty(i)) {
                    this.sentAcceptedList.push($.extend({}, optionsData.sentAcceptedList[i]));
                }
            }

            for (i in optionsData.sentNotAcceptedList) {
                if (optionsData.sentNotAcceptedList.hasOwnProperty(i)) {
                    this.sentNotAcceptedList.push($.extend({}, optionsData.sentNotAcceptedList[i]));
                }
            }

            if (optionsData.bill) {
                this.billData = $.extend(true, {}, optionsData.bill);

                this.url_print = '/get/' + this.billData.id + '/bill.html';
                this.url_pdf = '/get/' + this.billData.id + '/bill.pdf';
                this.billCreated = true;

                if (this.billData.status === 0) {
                    this.billStatusMessage = this.locales.statusNotPaid;
                }
            } else {
                this.billCreated = false;
            }

            this.canAskRecommendation = !optionsData.maxRequestCountReached;
            this.verifyRecNumber = optionsData.verifyRecNumber;
            this.initLayout();
        },

        onSendBillToEmail:function (e) {
            var that = this;
            $.ajax('/send_verify_bill/', {
                success:function (data) {
                    if (data.error) {
                        Y.Informer.show(that.locales.errorCantSendBill, 30);
                        console.error("Failed to send the bill: " + data.error);
                    } else {
                        Y.Modalbox.showSimple(that.locales.billSent);
                    }
                },
                error:function () {
                    Y.Informer.show(that.locales.errorCantSendBill, 30);
                },
                type:'POST',
                data:{
                    'bill_id':this.billData.id
                },
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
            return false;
        },

        onCreateInvoiceClick:function (e) {
            var thisView = this;

            function onSendAjaxSuccess(data) {
                var invoiceView;
                if (!data.error) {
                    // expected data:
                    // bill : {id, service_title, price, status, issued, number}
                    if (data.bill) {
                        thisView.billData = $.extend({}, data.bill);
                        thisView.url_print = '/get/' + data.bill.id + '/bill.html';
                        thisView.url_pdf = '/get/' + data.bill.id + '/bill.pdf';
                        thisView.billCreated = true;

                        if (thisView.billData.status === 0) {
                            thisView.billStatusMessage = thisView.locales.statusNotPaid;
                        }
                        invoiceView = new InvoiceView({
                            billCreated:true,
                            billData:thisView.billData,
                            billStatusMessage:thisView.billStatusMessage,
                            url_print:thisView.url_print,
                            url_pdf:thisView.url_pdf
                        });
                        thisView.$el.find('#invoice_view').html(invoiceView.render().el);
                    }
                } else {
                    Y.Informer.show(thisView.locales.errorCantCheckout, 30);
                }
            }

            $.ajax(e.currentTarget.pathname, {
                success:onSendAjaxSuccess,
                error:function () {
                    Y.Informer.show(thisView.locales.errorCantCheckout, 30);
                },
                type:'POST',
                data:{},
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });

            return false;
        }
    });

    Y.TabVerification = TabVerification;
}