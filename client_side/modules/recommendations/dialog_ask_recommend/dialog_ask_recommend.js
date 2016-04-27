function x(Y) {
    "use strict";

    Y.AskRecommendationsDialog = function(params) {
        this.url = params.url;
        this.ajaxSuccessCallback = params.success;
        this.ajaxErrorCallback = params.error;
        this.rek_id = params.rek_id;
        this.dialogTemplate = Y.TemplateStore.load('dialog_ask_recommend_dialog');
        this.locales = Y.Locales['dialog_ask_recommend_dialog'];

        this.show = function() {
            var that = this;
            Y.Modalbox.showCustom({
                buttons : [
                    {
                        'bcaption' : "Отправить",
                        'bstyle' : "action",
                        'callback' : function(valuesObj) {  // todo: rewrite logic, so we do not close this dialog in case of an error
                            $.ajax(that.url, {
                                success : that.ajaxSuccessCallback,
                                error : that.ajaxErrorCallback,
                                type:'POST',
                                data: {
                                    'rek_id': that.rek_id,
                                    'message':valuesObj['textarea[name=dialog-ta]']
                                },
                                dataType:'json',
                                beforeSend:function (jqXHR) {
                                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                                }
                            });
                    }
                },
                {'bcaption' : "Отмена", 'bstyle' : "simple"}],
                template : this.dialogTemplate,
                width: 500,
                inputNames : ['textarea[name=dialog-ta]']});
        };
    };
}
