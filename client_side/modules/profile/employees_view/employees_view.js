function x(Y) {
    "use strict";
    Y.ProfileEmployeesView = Backbone.View.extend({
        initialize : function() {
            this.$el.append($('<div>Employees <b>' + this.options.tab_content.someContent3 + '</b> ProfileEmployeesView</div>'));
        }
    });
}