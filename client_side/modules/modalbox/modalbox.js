function x(Y) {
    "use strict";

    var ModalboxBase, ModalboxSimple, ModalboxCustom, ModalboxHolder;

    ModalboxBase = Backbone.View.extend({
        message : '',
        template : null,
        $modal : null,
        modalboxid : null,
        callbacks : null,
        show : function(order) {
            this.render(order);
        },

        /* overridables, called from render() */
        activateModalbox : function() {
            return this.activateModalboxBase();
        },
        initButtons : function() {
            return this.initButtonsBase();
        },
        cleanSelf : function(backgroundFade) {
            var that = this, bgFadeMillisec = backgroundFade || 200;
            this.$modal.fadeOut(200, function() {
                that.$modal.remove();
            });
            $('div.#olap_' + this.modalboxid).fadeOut(bgFadeMillisec, function() {
                $('div#olap_' + that.modalboxid).remove();
            });
        },
        setParams : function(params) {
            this.message = params.message;
            this.template = params.template;
            this.modalboxid = params.id || this.generateIdFromTime();
            this.callbacks = params.callbacks || {};
        },

        /* internal methods */
        generateIdFromTime : function() {
            return (new Date()).getTime() % 2592000000;
        },
        getId : function() {
            return this.modalboxid;
        },
        getModalNode : function() {
            return $('div.modalbox#mb' + this.modalboxid);
        },

        render : function(order) {
            var windowHeight, dialogHeight, zOrder = order || 0;
            $('body').append('<div class="overlapformodal" id="olap_' + this.modalboxid + '"></div>');
            $('#olap_' + this.modalboxid).css('z-index', zOrder * 2 + 1000);
            this.activateModalbox();
            this.$modal = this.getModalNode();
            this.$modal.css('z-index', zOrder * 2 + 1001);
            this.initButtons();

            windowHeight = $(window).height();
            dialogHeight = this.getModalNode().height();
            if (dialogHeight >= windowHeight) {
                this.getModalNode().css({top:0});
            } else {
                this.getModalNode().css({top:(windowHeight - dialogHeight) / 2});
            }
        },
        activateModalboxBase : function() {
            $('body').append(this.template({ boxid : "mb" + this.modalboxid }));
            this.appendMessage();
        },
        appendMessage : function() {
            var messageblock = '', i, msglines = [];
            if(this.message instanceof Array) {
                for(i = 0; i < this.message.length; i += 1) {
                    msglines.push(this.wrapTextInParagraph(this.message[i]));
                }
                messageblock = msglines.join('');
            } else if(this.message) {
                messageblock = this.wrapTextInParagraph(this.message);
            }

            $('div.modalbox#mb' + this.modalboxid + ' div.modalbox-content').append(messageblock);
        },
        wrapTextInParagraph : function(text) {
            return '<p class="modalboxtext">' + text + '</p>';
        },
        initButtonsBase : function() {
            var that = this;
            this.getModalNode().find('div.modalbox-buttons').append('<a class="button action" id="buttonok' + this.modalboxid + '">OK</a>');
            this.getModalNode().find('a#buttonok').click(function() {
                Y.Modalbox.removeBox(that.modalboxid);
                return false;
            });
        }
    });


    ModalboxSimple = ModalboxBase.extend({
        buttons : [],
        setParams : function(params) {
            this.message = params.message;
            this.template = params.template;
            this.modalboxid = params.id || this.generateIdFromTime();
            this.buttons = params.buttons || [ { bstyle : "action", bcaption : "ОК" } ];
            this.width = params.width || 200;
            this.inputNames = params.inputNames || [];
        },
        activateModalbox : function() {
            this.activateModalboxBase();
            var outerbox = this.getModalNode(),
                leftMargin = (this.width + parseInt(outerbox.css('padding-left'), 10) +
                                parseInt(outerbox.css('padding-right'), 10)) / 2;
            outerbox.css("width", String(this.width) + "px");
            outerbox.css("margin-left",
                "-" + String(leftMargin) + "px");
        },
        initButtons : function() {
            var i, that = this,
                buttonblock = this.getModalNode().find('.modalbox-buttons');
            for(i = 0; i < this.buttons.length; i += 1) {
                this.addButton(buttonblock, this.buttons[i], i);
            }
            this.getModalNode().find('.cross-btn').click(function(e) {
                e.preventDefault();
                Y.Modalbox.removeBox(that.modalboxid);
                return false;
            });
        },
        wrapButtonHtml : function(btnelement, elindex) {
            return '<a id="modbtn' + elindex + '-' + this.modalboxid +
                        '" class="button ' + btnelement.bstyle + '">' + btnelement.bcaption + "</a>";
        },
        addButton : function(btnblock, btnelement, elindex) {
            var that = this,
                buttonnode,
                buttoncod = this.wrapButtonHtml(btnelement, elindex);
            btnblock.append(buttoncod);
            buttonnode = this.getModalNode().find('a#modbtn' + elindex + '-' + this.modalboxid);

            buttonnode.click(function() {
                var inputsData = {}, closeSelf = true;
                if(btnelement.callback) {
                    $.each(that.inputNames, function(i, name) {
                        inputsData[name] = that.getModalNode().find(name).val();
                    });
                    btnelement.callback(inputsData);
                    /* closeSelf = btnelement.callback(inputsData);
                    if(typeof(closeSelf) === 'undefined') {
                        closeSelf = true;
                    }*/
                    // todo: change logic to stand in case of error
                }
                if(closeSelf) {
                    Y.Modalbox.removeBox(that.modalboxid);
                }
                return false;
            });
        }
    });

    ModalboxCustom = ModalboxSimple.extend({
        templateParams : null,

        appendMessage : function() {},
        setParams : function(params) {
            this.message = params.message;
            this.template = params.template;
            this.modalboxid = params.id || this.generateIdFromTime();
            this.buttons = params.buttons || [ { bstyle : "action", bcaption : "ОК" } ];
            this.width = params.width || 200;
            this.inputNames = params.inputNames || [];
            this.templateParams = params.templateParams || {};
            this.customInitTemplate = params.customInitTemplate;
        },
        activateModalbox : function() {
            $('body').append(this.template($.extend({ boxid : "mb" + this.modalboxid }, this.templateParams)));
            if(this.customInitTemplate) {
                this.customInitTemplate(this);
            }
            var outerbox = this.getModalNode(),
                leftMargin = (this.width + parseInt(outerbox.css('padding-left'), 10) +
                    parseInt(outerbox.css('padding-right'), 10)) / 2;
            outerbox.css("width", String(this.width) + "px");
            outerbox.css("margin-left",
                "-" + String(leftMargin) + "px");
        }
    });

    ModalboxHolder = function() {
        this.modalSimpleClass = ModalboxSimple;
        this.modalCustomClass = ModalboxCustom;
        this.modalStack = [];
        this.simpleTemplate = Y.TemplateStore.load("modalbox_modal");

        this.lightExistingOverlap = function() {
            $('div.overlapformodal').addClass('overlapformodalbelow').removeClass('overlapformodal');
        };
        this.darkExistingOverlap = function() {
            $('div.overlapformodalbelow').addClass('overlapformodal').removeClass('overlapformodalbelow');
        };
        this.showSimple = function(message, buttonobj, width) {
            var simplebox = new this.modalSimpleClass();
            simplebox.setParams({ message : message, buttons : buttonobj,
                                    template : this.simpleTemplate, width : width });
            this.lightExistingOverlap();
            simplebox.show(this.modalStack.length);
            this.modalStack.push(simplebox);
        };
        this.showCustom = function(customparams) {
            var custombox = new this.modalCustomClass();
            custombox.setParams(customparams);
            this.lightExistingOverlap();
            custombox.show(this.modalStack.length);
            this.modalStack.push(custombox);
        };
        this.removeBox = function(boxid) {
            if(this.modalStack.length < 1) {
                throw new Error("Remove modal box error: modal boxes stack is empty!");
            }
            var boxToRemove = this.findBox(boxid), boxObj;
            if(boxToRemove === null) {
                throw new Error("Cannot remove modal box with boxid " + boxid + "!");
            } else {
                boxObj = this.modalStack[boxToRemove];
                this.modalStack.splice(boxToRemove, 1);
                boxObj.cleanSelf();
                if(boxToRemove === this.modalStack.length) {
                    this.darkExistingOverlap();
                }
            }
        };
        this.findBox = function(boxid) {
            var i, result = null;
            for(i = 0; i < this.modalStack.length; i += 1) {
                if(this.modalStack[i].getId() === boxid) {
                    result = i;
                    break;
                }
            }
            return result;
        };
    };

    Y.Modalbox = new ModalboxHolder();
}
