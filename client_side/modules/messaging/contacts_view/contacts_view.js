function x(Y) {
    "use strict";

    Y.ContactsView = Backbone.View.extend({
        initialize : function() {
            this.$el.append('<div style="color: maroon;">Contacts page</div>');
        }
    });
}