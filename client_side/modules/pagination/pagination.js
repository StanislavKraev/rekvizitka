function x(Y) {
    "use strict";

    Y.Paginator = Backbone.View.extend({

        events:{
            'click .paginator a' : 'onPaginatorClickPage'
        },

        paginatorHolder:Y.TemplateStore.load('pagination_holder'),

        paginatorTable:Y.TemplateStore.load('pagination_table'),

        paginatorTD:Y.TemplateStore.load('pagination_td'),

        inputData:null,

        html:null,

        paginatorHolderId : '',
        pagesSpan : '',
        baseUrl : '',
        el : null,
        $el : null,

        initialize : function() {
            this.paginatorHolderId = this.options.paginatorHolder;
            this.pagesSpan = this.options.pagesSpan;
            this.baseUrl = this.options.baseUrl;
            this.el = this.options.el;
            this.$el = $(this.el);
        },

        onPaginatorClickPage:function (eventObject) {
            var pageId = 0; // todo:
            this.trigger('clickPaginatorPage', pageId, eventObject.currentTarget.pathname + eventObject.currentTarget.search);
            return false;
        },

        render:function (pagesTotal, pageCurrent) {
            /*var paginatorHolderId = this.options.paginatorHolder,
                pagesSpan = this.options.pagesSpan,
                baseUrl = this.options.baseUrl,
                el = this.options.el;
            this.$el = $(el);*/

            pageCurrent = pageCurrent <= 0 ? 1 : pageCurrent;

            this.$el.empty().append(this.paginatorHolder({
                paginatorID:this.options.paginatorHolder
            }));

            if (!this.$el.find('#' + this.paginatorHolderId) || !pagesTotal || !this.pagesSpan) {
                return false;
            }

            this.inputData = {
                paginatorHolderId:this.paginatorHolderId,
                pagesTotal:pagesTotal,
                pagesSpan:(this.pagesSpan < pagesTotal) ? this.pagesSpan : pagesTotal,
                pageCurrent:pageCurrent,
                baseUrl:this.baseUrl
            };

            this.html = {
                holder:null,

                table:null,
                trPages:null,
                trScrollBar:null,
                tdsPages:null,

                scrollBar:null,
                scrollThumb:null,

                pageCurrentMark:null
            };

            this.prepareHtml();
            this.initScrollThumb();
            this.initPageCurrentMark();
            this.initEvents();
            this.scrollToPageCurrent();
            this.setPageCurrentPointWidth();
            this.movePageCurrentPoint();

            return this;
        },


        prepareHtml:function () {
            this.html.holder = this.$el.find('#' + this.inputData.paginatorHolderId);
            this.html.holder.html(this.makePagesTableHtml());

            this.html.table = this.$el.find('table');

            this.html.tdsPages = this.$el.find('.tr-pages td');

            this.html.scrollBar = this.$el.find('.scroll_bar');
            this.html.scrollThumb = this.$el.find('.scroll_thumb');
            this.html.pageCurrentMark = this.$el.find('.current_page_mark');

            if (this.inputData.pagesSpan >= this.inputData.pagesTotal) {
                this.html.holder.addClass('fullsize');
            }

            this.html.mainWidth = this.inputData.pagesTotal * 24;
        },

        /*
         Drag, click and resize events
         */
        initEvents:function () {
            var that = this;

            this.html.scrollThumb.mousedown(function (e) {

                $('body').mousemove(function (e) {

                    that.html.scrollThumb.xPos = e.pageX - that.html.table.offset().left - that.html.scrollThumb[0].offsetWidth / 2;

                    // the first: draw pages, the second: move scrollThumb (it was logically but ie sucks!)
                    that.moveScrollThumb();
                    that.drawPages();
                });

                $('body').mouseup(function () {
                    $('body').unbind('mousemove');
                });
            });

//            this.html.table.mouseleave(function(){
//                $('body').unbind('mousemove');
//            });

        },

        bindChangePageEvent : function(method, context) {
            this.unbind('clickPaginatorPage', method);
            this.bind('clickPaginatorPage', method, context);
        },

        drawPages:function () {
            var percentFromLeft = this.html.scrollThumb.xPos / (this.html.mainWidth),
                cellFirstValue = Math.round(percentFromLeft * this.inputData.pagesTotal),
                html = "", i, cellCurrentValue;

            // drawing pages control the position of the scrollThumb on the edges!
            if (cellFirstValue < 1) {
                cellFirstValue = 1;
                this.html.scrollThumb.xPos = 0;
                this.moveScrollThumb();
            } else if (cellFirstValue >= this.inputData.pagesTotal - this.inputData.pagesSpan) {
                cellFirstValue = this.inputData.pagesTotal - this.inputData.pagesSpan + 1;
                this.html.scrollThumb.xPos = this.html.table[0].offsetWidth - this.html.scrollThumb[0].offsetWidth;
                this.moveScrollThumb();
            }

            for (i = 0; i < this.html.tdsPages.length; i += 1) {
                cellCurrentValue = cellFirstValue + i;
                if (cellCurrentValue === this.inputData.pageCurrent) {
                    html = "<a class='current'>" + cellCurrentValue + "</a>";
                } else {
                    html = "<a href='" + this.inputData.baseUrl(cellCurrentValue) + "'>" + cellCurrentValue + "</a>";
                }
                this.html.tdsPages[i].innerHTML = html;
            }
        },

        scrollToPageCurrent:function () {
            this.html.scrollThumb.xPosPageCurrent = (this.inputData.pageCurrent - Math.round(this.inputData.pagesSpan / 2)) / this.inputData.pagesTotal * this.html.table[0].offsetWidth;
            this.html.scrollThumb.xPos = this.html.scrollThumb.xPosPageCurrent;

            this.moveScrollThumb();
            this.drawPages();
        },

        initScrollThumb:function () {
            this.html.scrollThumb.widthMin = '8'; // minimum width of the scrollThumb (px)
            this.html.scrollThumb.widthPercent = this.inputData.pagesSpan / this.inputData.pagesTotal * 100;

            this.html.scrollThumb.xPosPageCurrent = (this.inputData.pageCurrent - Math.round(this.inputData.pagesSpan / 2)) / this.inputData.pagesTotal * this.html.table[0].offsetWidth;
            this.html.scrollThumb.xPos = this.html.scrollThumb.xPosPageCurrent;

            this.html.scrollThumb.xPosMin = 0;

            this.setScrollThumbWidth();
        },

        setScrollThumbWidth:function () {
            // Try to set width in percents
            this.html.scrollThumb.css('width', this.html.scrollThumb.widthPercent + "%");

            // Fix the actual width in px
            this.html.scrollThumb.widthActual = this.html.scrollThumb[0].offsetWidth;

            // If actual width less then minimum which we set
            if (this.html.scrollThumb.widthActual < this.html.scrollThumb.widthMin) {
                this.html.scrollThumb.css('width', this.html.scrollThumb.widthMin + 'px');
            }

            this.html.scrollThumb.xPosMax = this.html.table[0].offsetWidth - this.html.scrollThumb.widthActual;
        },

        moveScrollThumb:function () {
            this.html.scrollThumb.css('left', this.html.scrollThumb.xPos + "px");
        },

        makePagesTableHtml:function () {
            var tdWidth = (100 / this.inputData.pagesSpan) + '%', i,
                html = '';

            for (i = 1; i <= this.inputData.pagesSpan; i += 1) {
                html += this.paginatorTD({
                    tdWidth:tdWidth
                });
            }

            html = this.paginatorTable({
                paginatorTDlist:html,
                pagesSpan:this.inputData.pagesSpan
            });

            return html;
        },

        initPageCurrentMark:function () {
            this.html.pageCurrentMark.widthMin = '3';
            this.html.pageCurrentMark.widthPercent = 100 / this.inputData.pagesTotal;

//            this.setPageCurrentPointWidth();
//            this.movePageCurrentPoint();
        },

        setPageCurrentPointWidth:function () {
            this.html.pageCurrentMark.css('width', this.html.pageCurrentMark.widthPercent + '%');
            this.html.pageCurrentMark.widthActual = this.html.pageCurrentMark[0].offsetWidth;
            if (this.html.pageCurrentMark.widthActual < this.html.pageCurrentMark.widthMin) {
                this.html.pageCurrentMark.css('width', this.html.pageCurrentMark.widthMin + 'px');
            }
        },

        movePageCurrentPoint:function () {
            var left = (this.html.table.width() / this.inputData.pagesTotal) * this.inputData.pageCurrent - this.html.pageCurrentMark.width();

            if (left >= (this.html.table.width() - this.html.pageCurrentMark.width())) {
                left = this.html.table.width() - this.html.pageCurrentMark.width();
            }
            this.html.pageCurrentMark.css('left', left + "px");
        }

    });

}