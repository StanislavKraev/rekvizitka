function x(Y) {
    "use strict";

    var OfficeEditView = Backbone.View.extend({

        valuesOffice:{},

        template:Y.TemplateStore.load('profile_contacts_view_offices_edit'),

        events:{
            'click a.remove':'removeOffice'
        },

        initialize:function () {
            this.valuesOffice = this.options.data;
            this.parentView = this.options.parentView;
        },

        render:function () {
            var uploader, thisView = this;

            this.$el.html(this.template(this.options.data));

            uploader = new qq.FileUploaderBasic({
                button:$('a.button', thisView.$el)[0],
                action:'/grid/send/profile/contactmap',
                multiple:false,
                sizeLimit:1024 * 1024,
                onComplete:function (id, filename, data) {
                    thisView.onComplete(id, filename, data);
                },
                restrictedExtensions:['exe', 'com'],
                messages:{
                    typeError:"Тип файла {file} не доступен для загрузки.",
                    sizeError:"Размер файла {file} превышает допустимый размер {sizeLimit}.",
                    minSizeError:"{file} is too small, minimum file size is {minSizeLimit}.",
                    emptyError:"{file} is empty, please select files again without it.",
                    onLeave:"The files are being uploaded, if you leave now the upload will be cancelled."
                }
            });

            return this;
        },

        onComplete:function (id, filename, data) {
            this.valuesOffice.imgID = data.imgID;

            $('.office-map', this.$el).attr({'src':data.imgUrl + '?r=' + Math.random(),
                width:data.width,
                height:data.height});
        },

        removeOffice:function () {
            this.$el.remove();
            this.parentView.removeOffice(this);
            return false;
        },

        getData:function () {
            return {
                'city':$('.nameOffice', this.$el).val(),
                'information':$('.taOffice', this.$el).val(),
                'informationHTML':Y.utils.wrapEachLine(Y.utils.escapeStr($('.taOffice', this.$el).val()), '', '<br>'),
                'imgID':this.valuesOffice.imgID
            };

        }

    });

    /**********************************************************************************************************/

    Y.ProfileContactsView = Backbone.View.extend({

        tabContent:{},

        newOffice:{
            city:'',
            information:'',
            informationHTML:'',
            imgID:'',
            img_src:'/media/i/default_image.png',
            img_width:'560',
            img_height:'340'
        },
        template:Y.TemplateStore.load('profile_contacts_view_content'),
        template_offices:Y.TemplateStore.load('profile_contacts_view_offices'),
        template_edit:Y.TemplateStore.load('profile_contacts_view_content_edit'),
        template_content_bottom:Y.TemplateStore.load('profile_contacts_view_content_bottom'),
        officeViewList:[],

        initialize:function () {
            this.initLayout();

            $('#contacts').on('click', 'a.edit', {'thisView':this}, this.startEdit);
            $('#contacts').on('click', 'a.save', {'thisView':this}, this.startSave);
            $('#contacts').on('click', 'a.cancel', {'thisView':this}, this.cancelEdit);
            $('#contacts').on('click', 'a.add', {'thisView':this}, this.addOffice);
        },

        addOffice:function (e) {
            var thisView = e.data.thisView, officeEdit, newOffice = {};

            $.extend(newOffice, e.data.thisView.newOffice);

            if (!thisView.tabContent.offices) {
                $.extend(thisView.tabContent, {offices:[]});
            }

            thisView.tabContent.offices.push(thisView.newOffice);

            officeEdit = new OfficeEditView({
                'data':newOffice,
                'parentView':thisView
            });

            thisView.officeViewList.push(officeEdit);

            thisView.$el.find('.bottom').before(officeEdit.render().el);

            return false;
        },

        startEdit : function (e) {
            var thisView = e.data.thisView, i, officeEdit;

            thisView.tabContent.descrHTML = thisView.tabContent.descr;

            thisView.$el.empty().append(thisView.template_edit(thisView.tabContent));

            for (i in thisView.tabContent.offices) {
                if (thisView.tabContent.offices.hasOwnProperty(i)) {

                    thisView.tabContent.offices[i].informationHTML = thisView.tabContent.offices[i].information;

                    officeEdit = new OfficeEditView({
                        'data':thisView.tabContent.offices[i],
                        'parentView':thisView
                    });
                    thisView.officeViewList.push(officeEdit);
                    thisView.$el.append(officeEdit.render().el);
                }
            }

            thisView.$el.append(thisView.template_content_bottom());

            return false;
        },

        removeOffice : function (officeView) {
            var index;
            for (index = 0; index < this.officeViewList.length; index += 1) {
                if (officeView === this.officeViewList[index]) {
                    this.officeViewList.splice(index, 1);
                    break;
                }
            }
        },

        startSave : function (e) {
            var thisView = e.data.thisView, data, office, officeData,
                linkProfileAplication = e.data.thisView.options.thisProfileApplication;

            data = {
                main_email:$('.edit-mode dd input#email').val(),
                main_site:$('.edit-mode dd input#site').val(),
                main_phone:$('.edit-mode dd input#phone').val(),
                offices: []
            };

            for (office in thisView.officeViewList) {
                if (thisView.officeViewList.hasOwnProperty(office)) {
                    officeData = thisView.officeViewList[office].getData();
                    data.offices.push(officeData);
                }
            }

            data = JSON.stringify(data);

            linkProfileAplication.moduleProcessContacts(data, e.data.thisView);

            return false;
        },

        cancelEdit : function (e) {
            var thisView = e.data.thisView, i;

            thisView.$el.empty().append(thisView.template(thisView.tabContent));

            for (i in thisView.tabContent.offices) {
                if (thisView.tabContent.offices.hasOwnProperty(i)) {
                    thisView.$el.append(thisView.template_offices(thisView.tabContent.offices[i]));
                }
            }

            return false;
        },

        initLayout : function () {
            var i, tab = this.options.thisProfileApplication.appSettings;

            this.tabContent = $.extend(tab.contacts, {
                own_company : tab.own_company
            });

            this.$el.append(this.template(this.tabContent));

            for(i in tab.contacts.offices) {
                if(tab.contacts.offices.hasOwnProperty(i)) {
                    if(tab.contacts.offices[i].imgID==='') {
                        tab.contacts.offices[i].img_height = this.newOffice.img_height;
                        tab.contacts.offices[i].img_width = this.newOffice.img_width;
                        tab.contacts.offices[i].img_src = this.newOffice.img_src;
                    }
                    tab.contacts.offices[i].informationHTML = Y.utils.wrapEachLine(Y.utils.escapeStr(tab.contacts.offices[i].information || ''), '', '<br>');
                    this.$el.append(this.template_offices(tab.contacts.offices[i]));
                }
            }
        },

        reinitLayout : function () {
            this.$el.empty();
            this.initLayout();
        },

        setData : function (newData) {
            this.$el = newData.el || this.$el;
            this.el = this.$el[0];
            this.reinitLayout();
        }
    });
}
