function x(Y) {
    "use strict";

    var InformerElement, InformerHolder, informerOriginTop;

    InformerElement = Backbone.View.extend({
        message : '',
        showtime : 0,
        template : null,
        domp : null,
        timeoutid : null,

        initialize : function() {
            this.message = (this.options.text instanceof String) ? '' : this.options.text;
            this.showtime = (this.options.showtime instanceof Number) ? 0 : this.options.showtime;
            this.system = this.options.system || false;
            this.template = this.options.template;
        },
        show : function() {
            this.render();
            this.informerScrollHook();
            $(window).scroll(this.informerScrollHook);
        },
        render : function() {
            var elem = this;

            elem.activateInfobox();

            elem.domp = $('div.informer');
            informerOriginTop = parseInt(elem.domp.css('top'), 10);
            elem.domp.on('click', 'div.informer a', elem.evtHolderRemoveCurrent);

            if(elem.showtime > 0) {
                elem.timeoutid = setTimeout(function() {
                    elem.domp.fadeOut(1000, elem.evtHolderRemoveCurrent);
                    elem.removeTimeout();
                }, elem.showtime * 1000);
            }

            return this;
        },
        activateInfobox : function() {
            var elem = this, i, infopara,
                infotype = (this.system ? 'system' : 'manual');

            if(elem.message instanceof Array) {
                if(elem.message.length > 0) {
                    $('body').append(elem.template({ infotext : elem.message[0],
                                                        infotype : infotype }));
                    infopara = $('div.informer div div');
                    for(i = 1; i < elem.message.length; i += 1) {
                        infopara.append('<p>' + elem.message[i] + '</p>');
                    }
                }
            } else {
                $('body').append(elem.template({ infotext : elem.message, infotype : infotype }));
            }
        },
        evtHolderRemoveCurrent : function() {  // here must be eventObject, but now it's of no use
            Y.Informer.removeCurrent();
            return false;
        },
        removeTimeout : function() {
            if(this.timeoutid) {
                clearTimeout(this.timeoutid);
                this.timeoutid = null;
            }
        },
        informerScrollHook : function() {
            var winTop = $(window).scrollTop(),
                infoTop = (winTop > informerOriginTop ? 0 : informerOriginTop - winTop);
            $('div.informer').css('top', infoTop);
        },
        cleanEvents : function() {
            this.removeTimeout();
            this.domp.off('click', 'div.informer a');
            this.domp.stop();
            $(window).unbind('scroll', this.informerScrollHook);
            this.domp.remove();
        }
    });

    InformerHolder = function(Y) {
        this.infoElemClass = InformerElement;
        this.currentShowed = null;
        this.infoTemplate = Y.TemplateStore.load("informer_informer");
        this.show = function(text, showtime) {
            return this._show({ text : text, showtime : showtime,
                                   template : this.infoTemplate,
                                   system : false });
        };
        this.showSystem = function(text, showtime) {
            return this._show({ text : text, showtime : showtime,
                                   template : this.infoTemplate,
                                   system : true });
        };
        this._show = function(elemParams) {
            this.removeCurrent();
            var showelem = new this.infoElemClass(elemParams);
            // showelem.setParams(elemParams);
            showelem.show();
            this.currentShowed = showelem;
        };
        this.removeCurrent = function() {
            if(this.currentShowed) {
                this.currentShowed.cleanEvents();
                this.currentShowed = null;
            }
        };
    };

    Y.Informer = new InformerHolder(Y);
}
