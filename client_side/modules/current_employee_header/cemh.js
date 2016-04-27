function x(Y) {
    "use strict";

    Y.CurrentEmployeeHeader = Backbone.View.extend({
        model : null,

        template : Y.TemplateStore.load('cemh_content'),

        initialize:function () {
            this.model = this.options.data || {};
            _.extend(this.model, {
                brandNameCut :Y.utils.cutLongString(this.model.brandName, 50)
            });
        },

        render:function () {
            this.$el.html(this.template(this.model));
            return this;
        }
    });
}
