function x(Y) {
    "use strict";

    var MainHeader;

    MainHeader = Backbone.View.extend({

        template:Y.TemplateStore.load('main_header_main_header'),
        template_unauth:Y.TemplateStore.load('main_header_main_header_unauth'),
        template_unauth_wrap:Y.TemplateStore.load('main_header_main_header_unauth_wrap'),

        locale:Y.Locales['main_header'],

        initialize:function () {
            var that = this,
                wrappedPart,
                $notificationsTdEl,
                $contractorsTdEl,
                $messagesTdEl,
                notifier;
            if (!this.options.auth) {
                wrappedPart = this.template_unauth();
                this.$el.append(this.template_unauth_wrap({
                    "csrf_token" : this.options.csrf,
                    "wrapped" : wrappedPart
                }));
            } else {
                this.$el.append(this.template({
                    "brandName" : this.options.brandName,
                    "employeeProfileUrl" :Y.ApplicationRouter.updateRoute(this.options.employeeProfileUrl)
                }));
            }
            this.$el.find('td:not(.exit) a').click(function(eventObj){
				that.headerLinkClicked(eventObj.currentTarget.pathname);
				return false;
			});

            $notificationsTdEl = this.$el.find('td.notifications');
            $contractorsTdEl = this.$el.find('td.contractors');
            $messagesTdEl = this.$el.find('td.emails');

            notifier = new Y.GlobalNotifierUi({'$nofityEl' : $notificationsTdEl,
                                    '$contractorEl' : $contractorsTdEl,
                                    '$messageEl' : $messagesTdEl});

        },

        headerLinkClicked : function(url) {
            Y.ApplicationRouter.navigate(url, {trigger : true});
        }
    });

    Y.MainHeader = MainHeader;
}
