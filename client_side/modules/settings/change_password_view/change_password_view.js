function x(Y) {
    "use strict";

    var changePassFields = [ 'old' , 'new', 'new2' ];

    Y.ChangePasswordView = Backbone.View.extend({
        locales : Y.Locales['change_password_view'],
        globalLocales : Y.localesGlobal,
        template : Y.TemplateStore.load('change_password_view_content'),
        settingsApplication : null,

        initialize : function() {
            this.el = this.options.el;
            this.$el = $(this.el);
            this.settingsApplication = this.options.containerApplication;
            this.initLayout();
        },
        initLayout : function() {
            var templateData = {
                loc_current_password : this.locales.currentPassword,
                loc_new_password : this.locales.newPassword,
                loc_new_confirm : this.locales.newConfirm,
                loc_forgot_password : this.locales.forgotPassword,
                loc_button_save : this.globalLocales.buttons.save
            }, that = this;
            this.$el.empty();
            this.$el.append(this.template(templateData));
            this.$el.find('#change-password .save').click(function() {
                that.verifyAndSavePassword();
                return false;
            });
        },
        verifyAndSavePassword : function() {
            var cpValues = this.getFieldValues();
            this.resetErrors();
            if(cpValues['new'] !== cpValues.new2) {
                this.showErrorForField(this.locales.errorBadConfirm, 'new2');
            } else if(cpValues['new'].length < 6) {
                this.showErrorForField(this.locales.errorShortPassword, 'new');
            } else if(cpValues.old.length < 1) {
                this.showErrorForField(this.locales.errorNoCurrent, 'old');
            } else if(cpValues.old === cpValues['new']) {
                this.showErrorForField(this.locales.errorSameAsCurrent, 'new');
            } else {
                this.settingsApplication.saveNewPassword(cpValues, { that : this },
                        this.saveNewPasswordSuccess, this.saveNewPasswordFail);
            }
        },
        getFieldValues : function() {
            var valuesObj = {}, i;
            for(i in changePassFields) {
                if(changePassFields.hasOwnProperty(i)) {
                    valuesObj[changePassFields[i]] = this.$el.find('#' + changePassFields[i]).val();
                }
            }
            return valuesObj;
        },
        saveNewPasswordSuccess : function(params, data) {
            if(data.error) {
                params.that.showErrorForField(data.msg, data.loc || 'old');
            } else {
                Y.Informer.show(params.that.locales.saveNewPasswordSuccess, 10);
                params.that.$el.find('input').val('');
            }
        },
        saveNewPasswordFail : function(params) {
            Y.Informer.show(params.that.locales.errorBadConnect, 15);
        },
        showErrorForField : function(text, blockId) {
            this.$el.find('#' + blockId).addClass('error');
            this.$el.find('#' + blockId).parent().find('div.error').append(text);
        },
        resetErrors : function() {
            var i;
            for(i in changePassFields) {
                if(changePassFields.hasOwnProperty(i)) {
                    this.$el.find('#' + changePassFields[i]).removeClass('error');
                    this.$el.find('#' + changePassFields[i]).parent().find('div.error').empty();
                }
            }
        }
    });
}
