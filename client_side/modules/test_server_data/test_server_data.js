function x(Y) {
    "use strict";

    Y.testServerData = {
        findNonfilledProps : function(obj) {
            /*jslint forin: true*/
            var i, emptyProps = [];
            if(typeof(obj) === 'object') {
                for(i in obj) {
                    if(obj[i] === null) {
                        emptyProps[emptyProps.length] = i;
                    }
                }
            }
            return emptyProps;
        }
    };
}
