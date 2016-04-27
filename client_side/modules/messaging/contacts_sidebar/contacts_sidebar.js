function x(Y) {
    "use strict";

    Y.ContactsSidebarView = Backbone.View.extend({
        template : Y.TemplateStore.load('contacts_sidebar_sidebar'),
        initialize : function() {
            this.sid = this.options.sid;
        },
        render : function() {
            this.$el.append(this.template());
            return this;
        },
        show : function() {
            this.$el.show();
        },
        hide : function() {
            this.$el.hide();
        }
    });
}