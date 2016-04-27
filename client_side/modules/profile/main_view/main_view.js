function x(Y) {
    "use strict";
    Y.ProfileMainView = Backbone.View.extend({
        initialize : function() {
            this.$el.append($('<div>Profile</div>'));
        }
    });
}