function x(Y) {
    "use strict";

    var GlobalNotifier, Audio;

    /* Events                                                               */

    /* -------------------------------------------------------------------- */
    /*      unreadMessageCountChanged                                       */
    /*  params:                                                             */
    /*      unreadDialogsNewCount                                           */
    GlobalNotifier = {
        notificationsState : {
            unreadMessages : 0
        },

        start : function(notificationsObj) {
            Y.ChatDialogManager.connectToServer();
            Y.ChatDialogManager.on("unreadMessageCountChanged", this.onUnreadMessageCountChanged, this);
            if (notificationsObj) {
                if (notificationsObj.hasOwnProperty('unread_dialogs')) {
                    this.notificationsState.unreadMessages = notificationsObj.unread_dialogs;
                }
            }
        },

        onUnreadMessageCountChanged : function(newCount) {
            this.trigger("unreadMessageCountChanged", newCount);
        }
    };
    _.extend(GlobalNotifier, Backbone.Events);

    Audio = function(audioFilesPath) {
        this.filePath = audioFilesPath;
        this.fileName = audioFilesPath.substring(audioFilesPath.lastIndexOf('/') + 1);
        this.audioBlockId = 'audioblock-' + this.fileName;
        this.placeAudio = function() {
            if(this.filePath) {
                $('body').find('#' + this.audioBlockId).remove();
                $('body').append('<audio id="' + this.audioBlockId + '" preload="auto">' +
                    '<source src="' + this.filePath + '.mp3" type="audio/mpeg"/>' +
                    '<source src="' + this.filePath + '.ogg" type="audio/ogg"/>' +
                    '<embed src="' + this.filePath + '.mp3"/>' +
                    '</audio>');
            }
        };
        this.placeAudio();

        this.play = function() {
            var audioBlock = $('body').find('#' + this.audioBlockId)[0];
            audioBlock.play();
        };
    };

    Y.GlobalNotifier = GlobalNotifier;
    Y.Audio = Audio;
}
