function x(Y) {
    "use strict";
    Y.ProfileSettingsView = Backbone.View.extend({

        timezones : [],
        values : {},
        prevcursor : '',

        template : Y.TemplateStore.load('profile_settings_view_content'),
        locales : Y.Locales['profile_settings_view'],

        initialize : function () {
            var tab = this.options.tab_content,
                uservalue = [ tab.current_tz_id || 1,
                                tab.current_tz_name || this.locales.defaultZone ];
            this.values = {
                timezone_select : [ uservalue ],
                user_timezone : uservalue[0]
            };

            this.$el.append(this.template(this.values));

            $('#settings-btns').on('click', 'a.save', { 'thisView' : this }, this.evStartSave);
            $('#mainsettzone').click({ 'thisView' : this }, this.evLoadAllZones);
        },

        evLoadAllZones : function(e) {
            var that = e.data.thisView;
            that.asyncLoadZonesIfNeeded();
            return false;
        },
        evStartSave : function (e) {
            var that = e.data.thisView;
            that.asyncSaveSettings();
            return false;
        },
        asyncSaveSettings : function() {
            var that = this,
                data = JSON.stringify({
                    'timezone_id' : $('#mainsettzone').val()
                });

            function onSendMainSettingsSuccess(data) {
                if (data.error) {
                    Y.Informer.show(that.locales.saveSettingsFailed, 10);
                } else {
                    Y.Informer.show(that.locales.saveSettingsSuccess, 10);
                }
            }

            $.ajax('/settings/edit/', {
                success : onSendMainSettingsSuccess,
                error : function () {
                    Y.Informer.show(that.locales.saveSettingsAjaxError, 10);
                },
                type : 'POST',
                data : { act :'gi', data : data },
                dataType : 'json',
                beforeSend : function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        },
        asyncLoadZonesIfNeeded : function() {
            var that = this;
            function loadZonesAjaxSuccess(ajaxResp) {
                if(ajaxResp.length > 0) {
                    that.timezones = ajaxResp;  // maybe it will be more convenient to save zones in Settings_init
                    var selectbox = $('#mainsettzone'), i,
                        userzone = that.values.user_timezone || 1;
                    for(i = 0; i < ajaxResp.length; i+= 1) {
                        selectbox.append('<option value="' + ajaxResp[i][0] + '"' +
                            (ajaxResp[i][0] === userzone ? ' selected ' : '') +
                            '>' + ajaxResp[i][1] + '</option>');
                    }
                } else {
                    Y.Informer.show(that.locales.loadZonesNoInfo, 10);
                }
                $('#mainsettzone').css('cursor', that.prevcursor);
            }

            if(this.timezones.length < 1) {
                this.prevcursor = $('#mainsettzone').css('cursor');
                $('#mainsettzone').empty('option');
                $('#mainsettzone').css('cursor', 'wait');

                $.ajax('/settings/s/zones/', {
                    success : loadZonesAjaxSuccess,
                    error : function() {
                        Y.Informer.show(that.locales.loadZonesFail, 10);
                        $('#mainsettzone').css('cursor', that.prevcursor);
                    },
                    type : "GET",
                    dataType : 'json'
                });
            }
        }

});
}