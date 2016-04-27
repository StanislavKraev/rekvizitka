function x(Y) {
    "use strict";

    Y.TabDeposit = Backbone.View.extend({

        values:{},

        template:Y.TemplateStore.load('tab_deposit_content'),

        templateTable:Y.TemplateStore.load('tab_deposit_table'),

        templateTr:Y.TemplateStore.load('tab_deposit_table_tr'),

        initialize:function () {
            var tab = this.options.tab_content, html = '', x, income, expenditure;

            for (x in tab.history) {
                if (tab.history.hasOwnProperty(x)) {
                    income = '';
                    expenditure = '';

                    if (tab.history[x][1] > 0) {
                        income = tab.history[x][1];
                    } else {
                        expenditure = tab.history[x][1];
                    }

                    html += this.templateTr({
                        'date':tab.history[x][0],
                        'income':income,
                        'expenditure':expenditure,
                        'balance':tab.history[x][2],
                        'operation':tab.history[x][3]
                    });
                }
            }

            html = this.template(tab) + $(this.templateTable()).append(html)[0].outerHTML;

            this.$el.append(html);

        }
    });
}