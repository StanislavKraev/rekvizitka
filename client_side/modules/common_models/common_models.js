function x(Y) {
    "use strict";

    Y.CommonModels = {
        FolderItem : Backbone.Model.extend({
            defaults : {
                title : "",
                count : "",
                sid : ""
            }
        })
    };
}
