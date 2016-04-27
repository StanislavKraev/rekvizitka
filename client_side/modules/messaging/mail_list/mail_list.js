function x(Y) {
    "use strict";

    // Loading locale resources for current language
    var resources,
        MessageListView,
        MessageItemView;

    resources = Y.Locales['mail-list'];

    // Views
    MessageItemView = Backbone.View.extend({
        tagName : 'li',
        className: 'list',
        itemTemplate : Y.TemplateStore.load('mail-list_mail_list_item'),
        events : {
            'click div.important': 'setImportant'
        },
        render: function() {
            var html, model;

            model = this.model.toJSON();
            if (!model.hasOwnProperty('important')) {
                model.important = false;
            }
            if (!model.hasOwnProperty('official')) {
                model.official = false;
            }
            model.message_date_text = 'дата';
            model.from_company = 'компания';
            model.first_line = model.content;

            html = this.itemTemplate(model);
            $(this.el).html(html);
            return this;
        },

        removeView : function() {
            $(this.el).remove();
            this.model = null;
        },

        setImportant: function() {
            // todo: move implementation to manager
//            var importantUpdate, self = this, message_id = self.model.id;
//
//            importantUpdate= function(data){
//                var resultStatus = parseInt(data.result_status, 10);
//
//                switch(resultStatus){
//                    case 0: /*unknown_error*/
//                        break;
//                    case 1: /*user_not_found*/
//                        break;
//                    case 2: /*bad_request*/
//                        break;
//                    case 3: case 4: /*ok*/
//                        $(self.el).find('div.important').removeClass(String(self.model.attributes.is_important));
//                        self.model.attributes.is_important = resultStatus === 3;
//                        $(self.el).find('div.important').addClass(String(self.model.attributes.is_important));
//                        break;
//                    default: /*unknown_error*/
//                        break;
//                }
//            };
//
//            $.ajax({url:'/messages/letters/important/',
//                    success: importantUpdate,
//                    type:'POST',
//                    data: {'message_id':message_id},
//                    dataType: 'json',
//                    beforeSend : function(jqXHR) {
//                        jqXHR.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
//                    },
//                    error : function() {
//                        importantUpdate();
//                    }
//            });
        }
    });

    MessageListView = Backbone.View.extend({
        itemViews : [],
        mainTemplate : Y.TemplateStore.load('mail-list_mail_list'),
        events : {
        },
        $messageList : null,
        
        initialize : function() {
            $(this.options.domElementName).append(this.mainTemplate({"title" : resources.mail_list}));

            this.previewView = null;
            this.$el = $('div.m_mail_list');
            this.el = this.$el[0];

            this.$messageList = this.$el.find('ul');
        },

        clear : function() {
            var i, item;

            for (i = 0; i < this.itemViews.length; i += 1) {
                item = this.itemViews[i];
                item.removeView();
            }
            this.itemViews = [];
        },

        setItems : function(items) {
            this.clear();
            this.itemViews = [];

            var i, itemView, item;

            for (i = 0; i < items.length; i += 1) {
                item = items[i];
                itemView = new MessageItemView({model : item});
                this.itemViews.push(itemView);
                this.$messageList.append(itemView.render().el);
            }
        }
    });

    Y.MailList = MessageListView;
}
