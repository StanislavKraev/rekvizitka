function x(Y) {
    "use strict";

    function TemplateStore() {
        this.templates = {};
    }

    TemplateStore.prototype.load = function (name) {
        return this.templates[name];
    };

    TemplateStore.prototype.store = function(name, template) {
        if (this.templates.hasOwnProperty(name)) {
            return;
        }
        this.templates[name] = template;
    };
    Y.TemplateStore = new TemplateStore();
}