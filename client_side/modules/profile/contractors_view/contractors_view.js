function x(Y) {
    "use strict";
    Y.ProfileContractorsView = Backbone.View.extend({
        initialize : function() {
            this.$el.append($('<div>Contractors</div>'));
        }
    });
}