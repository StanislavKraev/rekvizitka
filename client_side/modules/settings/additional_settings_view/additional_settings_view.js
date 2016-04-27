function x(Y) {
    "use strict";
    Y.ProfileAdditionalSettingsView = Backbone.View.extend({

	values : {},

        template : Y.TemplateStore.load('profile_additional_settings_view_content'),

///        template_edit : Y.TemplateStore.load('additional_settings_view_content_edit'),

        initialize : function() {
		var tab = this.options.tab_content, read_mode, thisView = this, uploader;

		this.$el.append(this.template(tab));
        }

    });
}