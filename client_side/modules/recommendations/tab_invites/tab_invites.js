function x(Y) {
    "use strict";
    var SentListView, SentRegisteredListView, TabInvites,
        locales = Y.Locales['tab_invites'];

    SentRegisteredListView = Backbone.View.extend({
        tagName:"span",
        values:{},
        template_sent_registered_list_li:Y.TemplateStore.load('tab_invites_registered_list_li'),

        render:function () {
            this.$el.append(this.template_sent_registered_list_li(this.options.data));
            return this;
        }
    });

    SentListView = Backbone.View.extend({
        tagName:"li",
        values:{},
        template_sent_list_li:Y.TemplateStore.load('tab_invites_sent_list_li'),

        render:function () {
            this.$el.append(this.template_sent_list_li(this.options.data));
            return this;
        }
    });

    TabInvites = Backbone.View.extend({
        sentList: null,
        sentRegisteredList: null,
        sentListViews: null,
        template:Y.TemplateStore.load('tab_invites_content'),
        template_sent_list:Y.TemplateStore.load('tab_invites_sent_list'),
        template_registered_list:Y.TemplateStore.load('tab_invites_registered_list'),
        locales :Y.Locales['tab_invites'],

        events:{
            "click a.invite":"onSendInvite"
        },

        initialize:function () {
            var i, optionsData = this.options.tabContent, sentList, sentRegisteredList;
            this.sentList = [];
            this.sentRegisteredList = [];
            this.sentListViews = [];
            sentList = optionsData.sentList || [];
            sentRegisteredList = optionsData.sentRegisteredList || [];
            for (i in sentList) {
                if (sentList.hasOwnProperty(i)) {
                    this.sentList.push($.extend(true, {}, sentList[i]));
                }
            }
            for (i in sentRegisteredList) {
                if (sentRegisteredList.hasOwnProperty(i)) {
                    this.sentRegisteredList.push($.extend(true, {}, sentRegisteredList[i]));
                }
            }

            this.initLayout();
        },

        appendSentList:function () {
            var view, i, html = '',
                sent_invites_header, sent_registered_invites_header;

            if (this.sentList.length) {
                sent_invites_header = 'strings';
            }

            if (this.sentRegisteredList.length) {
                sent_registered_invites_header = this.locales.infoInvitationsSent + " " +
                    this.sentRegisteredList.length + ' ' +
                    Y.utils.morph('компания', this.sentRegisteredList.length, 'd');
            }

            /* this.$el.append(
                this.template({
                    'sent_invites_header':sent_invites_header || '',
                    'sent_registered_invites_header':sent_registered_invites_header || ''
                })
            ); */

            if (this.sentList.length) {
                for (i in this.sentList) {
                    if (this.sentList.hasOwnProperty(i)) {
                        view = new SentListView({
                            'data':this.sentList[i]
                        });
                        this.sentListViews.push(view);
                        html += view.render().el.outerHTML;
                    }
                }
                html = this.template_sent_list({
                    sentListHeader:locales.sentListHeader,
                    sentListUL:html
                });
            }
            return html;
        },

        appendRegisteredList:function () {
            var view, i, arr = [], html = '';

            if (this.sentRegisteredList.length) {

                for (i in this.sentRegisteredList) {
                    if (this.sentRegisteredList.hasOwnProperty(i)) {
                        view = new SentRegisteredListView({
                            'data':this.sentRegisteredList[i]
                        });
                        arr.push(view.render().el.outerHTML);
                    }
                }

                html = this.template_registered_list({
                    registeredListText:locales.registeredListText,
                    registeredListQTY:this.sentRegisteredList.length,
                    companies: Y.utils.morph(locales.company, this.sentRegisteredList.length, 'v'),
                    registeredList:arr.join(', ')
                });

            }
            return html;
        },

        initLayout:function () {
            this.$el.empty().append(this.template({
                sentList:this.appendSentList(),
                registeredList:this.appendRegisteredList()
            }));
            this.$el.on('click', 'a.registered-invite', this, function(eventObject) {
                var url = eventObject.currentTarget.pathname + eventObject.currentTarget.search;
                Y.ApplicationRouter.navigate(url, {trigger:true});
                return false;
            });
        },

        setData:function (newData) {
        },

        onSendInvite:function () {
            var thisView = this, email, message, d, m, y;

            function onSendAjaxSuccess(data) {
                var view, today;

                if (data.error || data.email_exists) {
                    if (data.email_exists) {
                        Y.Informer.show(thisView.locales.errorEmailExists, 30);
                    } else {
                        Y.Informer.show(thisView.locales.errorCantSendInvite, 20);
                        console.error("Failed to send the invitation: " + data.error);
                    }
                } else {
                    today = new Date();
                    d = today.getDate().toString();
                    m = (today.getMonth() + 1).toString();
                    y = (today.getFullYear()).toString();
                    if (d.length === 1) {
                        d = '0' + d;
                    }
                    if (m.length === 1) {
                        m = '0' + m;
                    }

//                    view = new SentListView({
//                        'data':{
//                            'email':$('#input-email', thisView.$el).val(),
//                            'date':d + "." + m + "." + y
//                        }
//                    });

                    thisView.sentList.push({
                        'email':$('#input-email', thisView.$el).val(),
                        'date':d + "." + m + "." + y
                    });

                    if (thisView.$el.has('.sent-list')){
                        thisView.$el.find('.sent-list').replaceWith(thisView.appendSentList());
                    }else{
                        thisView.$el.append(thisView.appendSentList());
                    }

                    $('#input-email', thisView.$el).val('');
                    $('#textarea-message', thisView.$el).val('');
                    Y.Modalbox.showSimple(thisView.locales.invitationSent);
                }
            }

            email = $('#input-email', thisView.$el).val();
            message = $('#textarea-message', thisView.$el).val();

            if (Y.utils.is_correct_email(email).length) {
                Y.Informer.show(thisView.locales.reenterEmail, 20);
                return false;
            }

            if (!message.length) {
                Y.Informer.show(thisView.locales.reenterMessage, 15);
                return false;
            }

            $.ajax('/invites/send/', {
                success:onSendAjaxSuccess,
                error:function () {
                    Y.Informer.show(thisView.locales.errorCantSendInvite, 10);
                },
                type:'POST',
                data:{
                    'email':email,
                    'msg':message
                },
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });

            return false;
        }
    });
    Y.TabInvites = TabInvites;
}