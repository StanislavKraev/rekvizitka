function x(Y) {
    "use strict";

    var GlobalNotifierUi;

    GlobalNotifierUi = Backbone.View.extend({
        im_sound : new Y.Audio("/media/mp3/im"),
        suppress : true,
        messageCount : 0,
        initialize : function() {
            this.$nofityEl = this.options.$nofityEl;
            this.$contractorEl = this.options.$contractorEl;
            this.$messageEl = this.options.$messageEl;
            this.updateState();
            Y.GlobalNotifier.on("unreadMessageCountChanged", this.onUnreadMessageCountChanged, this);
            this.suppress = false;
        },

        updateState : function() {
            this.onUnreadMessageCountChanged(Y.GlobalNotifier.notificationsState.unreadMessages);
        },

        onUnreadMessageCountChanged : function(newCount) {
            this.$messageEl.find('span').text(newCount || '');
            this.$messageEl.removeClass('unread');
            if (newCount) {
                this.$messageEl.addClass('unread');
                if ((this.messageCount < newCount) && !this.suppress) {
                    this.im_sound.play();
                }
            }
            this.messageCount = newCount;
        }
    });

    Y.GlobalNotifierUi = GlobalNotifierUi;
}
