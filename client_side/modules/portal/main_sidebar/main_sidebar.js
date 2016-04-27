function x(Y) {
    "use strict";

    var SidebarView,
        FeedbackSidebarView,
        SearchSidebarView,
        CompanyProfileSidebarView,
        BaseNoSidebarView,
        BaseSidebarView;

    BaseNoSidebarView = Backbone.View.extend({
        initialize:function () {
            $('.layout').addClass('no-left-sidebar');
        }
    });

    BaseSidebarView = Backbone.View.extend({
        initialize:function () {
            $('.layout').removeClass('no-left-sidebar');
        }
    });

    FeedbackSidebarView = BaseNoSidebarView.extend({});

    SearchSidebarView = BaseSidebarView.extend({
        className:'search-sidebar',
        locale:Y.Locales['main_sidebar'],
        template:Y.TemplateStore.load('main_sidebar_search_sidebar'),
        template_li:Y.TemplateStore.load('main_sidebar_search_li'),
        list:[
            {'href':'href1', 'title':'Компании'}
//            ,{'href' : 'href2','title' : 'Люди'},
//			{'href' : 'href3','title' : 'Сообщества'}
        ],

        render:function () {
            var $sidebar, list = '', that = this,
                main_data = {small_business_title:this.locale.small_business_title,
                    startup_title:this.locale.startup_title,
                    social_project_title:this.locale.social_project_title,
                    cat_small:$.inArray("small", this.options.categories) !== -1,
                    cat_startup:$.inArray("startup", this.options.categories) !== -1,
                    cat_social_project:$.inArray("social_project", this.options.categories) !== -1
                };

            $sidebar = this.$el.append(this.template(main_data));
            $.each(this.list, function (id, li_item) {
                list += that.template_li(li_item);
            });
            $sidebar.on('click', 'input', this, function (eventObject) {
                var name = this.name,
                    that = eventObject.data,
                    state = $(this).attr('checked');

                that.trigger('company_category_checked', name, state);
            });

            $sidebar.find('ul#my-search-list').html(list);
            $sidebar.find('ul#my-search-list li').first().addClass('current');
            return this;
        }
    });

    CompanyProfileSidebarView = BaseSidebarView.extend({
        className:'common-sidebar',

        template:Y.TemplateStore.load('main_sidebar_sidebar'),
        template_ul:Y.TemplateStore.load('main_sidebar_sidebar_ul'),
        template_li:Y.TemplateStore.load('main_sidebar_sidebar_li'),
        template_contractors:Y.TemplateStore.load('main_sidebar_contractors'),
        template_contractors_ul:Y.TemplateStore.load('main_sidebar_contractors_ul'),
        template_contractors_li:Y.TemplateStore.load('main_sidebar_contractors_li'),
        template_edit_logo:Y.TemplateStore.load('main_sidebar_edit_logo'),
        template_loader:Y.TemplateStore.load('main_sidebar_loader'),

        locale:Y.Locales['main_sidebar'],
        LG:Y.localesGlobal,

        defaultLogo:'/media/i/default_company_page.png',

        defaultLogoOwn:'/media/i/default_logo.png',

        currentAvatar:'',

        initialize:function () {
            BaseSidebarView.prototype.initialize.call(this);
            Y.utils.preloadImages('/media/i/ajax_loader.gif');
        },

        render:function () {
            var $sidebar, thisView = this, list, our_partner,
                uploader, sidebarVars,
                li_items, li_item,
                template_ul_args, li_args, item_data,
                contractors_base_args, ul_item,
                sidebar_lists, recommendation_title, logo, profile_title, partners_title;

            /*	AVATAR BLOCK		*/

            if (this.options.own) {
                this.currentAvatar = this.defaultLogoOwn;
            } else {
                this.currentAvatar = this.defaultLogo;
            }

            our_partner = this.options.we_are_partners === 'yes' ||
                            this.options.we_are_partners === 'we_asked' ||
                            this.options.we_are_partners === 'they_declined';
            sidebarVars = {
                'img':{
                    src:this.options.avatar || this.currentAvatar,
                    alt:""
                },
                'file_upload_title':this.options.avatar ? this.locale.change_logo : this.locale.add_logo,
                'kind_of_hint':this.options.avatar ? 'change-logo' : 'add-logo',
                'logo_type':'',
                'send_msg' : !this.options.own && this.options.verified,
                'own':this.options.own,
                'eid':this.options.employee_id,
                'authorized' : this.options.authorized,
                'can_add_partner' : !this.options.own && !our_partner && this.options.verified
            };

            if(this.options.own && !this.options.avatar){
                sidebarVars.logo_type = 'empty-logo';
            }else{
                sidebarVars.logo_type = 'exist-logo';
            }

            $sidebar = this.$el.append(this.template(sidebarVars));
            recommendation_title = this.locale.recommendations;
            profile_title = this.locale.company_profile;
            partners_title = this.locale.partners;

            if (this.options.own) {
                recommendation_title = this.locale.our_recommendations;
                profile_title = this.locale.my_company_profile;
                partners_title = this.locale.our_partners + (this.options.nonviewed > 0 ? ' (' + this.options.nonviewed + ')' : '');
            }

            /* LISTS */
            sidebar_lists = {
//                    my_profile:{
//                        ul_class:'my-profile-list',
//                        list:{
//					profile:{
//						href:'url to my profile',
//						id:'my-profile-home',
//						title:locale.my_profile
//					},
//					news:{
//						href:'url to news',
//						id:'my-profile-news',
//						title:locale.news
//					},
//					emails:{
//						href:'url to emails',
//						id:'my-profile-emails',
//						title:locale.emails
//					},
//					my_subscribes:{
//						href:'url to ',
//						id:'my-subscribes',
//						title:locale.my_subscribes
//					}
//                        }
//                    },
                company_profile:{
                    ul_class:'company-profile-list',
                    list:{
                        profile:{
                            href:Y.ApplicationRouter.updateRoute(this.options.rek_id + '/profile/'),
                            id:'profile',
                            title:profile_title
                        },
                        deposit:{
                            href:Y.ApplicationRouter.updateRoute('deposit/'),
                            id:'deposit',
                            title:this.locale.deposit
                        },
                        partners:{
                            href:Y.ApplicationRouter.updateRoute(this.options.rek_id + '/contractors/'),
                            id:'partners',
                            title:partners_title
                        },
                        our_proposers:{
                            href:Y.ApplicationRouter.updateRoute(this.options.rek_id + '/our_proposers/'),
                            id:'our_proposers',
                            title:recommendation_title
                        }
//
//                        contractors:{
//                            href:'/' + this.options.rek_id + '/contractors',
//                            id:'l_contractors',
//                            title:this.locale.contractors
//                        },
//                        company_subscribers:{
//                            href:'url to ',
//                            id:'company-subscribers',
//                            title:this.locale.company_subscribers
//                        },
//                        communities:{
//                            href:'url to ',
//                            id:'communities',
//                            title:this.locale.communities
//                        },
//                        tenders:{
//                            href:'url to ',
//                            id:'tenders',
//                            title:this.locale.tenders
//                        }
                    }
                }
            };

            if (thisView.options.own) {
                sidebar_lists.company_profile.list['chat'] = {
                    href:Y.ApplicationRouter.updateRoute('chat/'),
                    id:'chat',
                    title:this.locale.chat
                };
            }

            for (ul_item in sidebar_lists) {
                if (sidebar_lists.hasOwnProperty(ul_item)) {
                    li_items = sidebar_lists[ul_item].list;
                    template_ul_args = {'ul_class':sidebar_lists[ul_item].ul_class || ""};
                    $sidebar.append(this.template_ul(template_ul_args));
                    list = '';

                    for (li_item in li_items) {
                        if (li_items.hasOwnProperty(li_item)) {
                            if (li_item === 'deposit' && !thisView.options.own) {
                                item_data = '';  // todo: make more elegant code
                            } else {
                                item_data = li_items[li_item];

                                li_args = {
                                    'href':item_data.href || "",
                                    'title':item_data.title || "",
                                    'itemid' : 'mc_sidebar_' + li_item,
                                    'current':li_item === this.options.sidebarID ? 'class="current"' : ''
                                };

                                list += this.template_li(li_args);
                            }
                        }
                    }

                    $sidebar.find('ul.' + sidebar_lists[ul_item].ul_class, $sidebar).html(list);
                }
            }

            $sidebar.on('click', 'a.add-to-contractor-request', {'that':this}, function (eventObject) {
                eventObject.data.that.ajaxAddPartnerRequest({
                    'post' : {
                        'rek_id':eventObject.data.that.options.rek_id
                    },
                    'eventObject':eventObject,
                    'neededClass':'pushed',
                    'removedClass':'add-to-contractor-request',
                    'newText': eventObject.data.that.options.we_are_partners === 'they_asked' ?
                                    "Контрагент добавлен" : 'Заявка отправлена',
                    'url' : eventObject.data.that.options.we_are_partners === 'they_asked' ?
                                    '/contractors/accept/' : '/contractors/add/',
                    'action' : eventObject.data.that.options.we_are_partners === 'they_asked' ?
                                    'accept' : 'add'
                });
                return false;
            });

            $sidebar.on('click', 'a.sidebar', function (eventObject) {
                thisView.trigger('sidebarLinkClicked', {linkURL:eventObject.target.pathname});
                return false;
            });

            $sidebar.on('click', 'a.send', function (eventObject) {
                // thisView.trigger('sidebarLinkClicked', {linkURL:eventObject.target.pathname});
                Y.ApplicationRouter.navigate(eventObject.target.pathname, { replace : false, trigger : true });
                return false;
            });

            /*	CONTRACTORS		*/

            if (this.options.contractors && this.options.contractors.length) {
                contractors_base_args = {
                    'title':this.locale.contractors + ' (' + this.options.contractors.length + ')'
                };
                $sidebar = this.$el.append(this.template_contractors(contractors_base_args));
                $sidebar.append(this.template_contractors_ul({
                    'ul_class':'my-contractors-list'
                }));

                list = '';

                for (li_item in this.options.contractors) {
                    if (this.options.contractors.hasOwnProperty(li_item)) {
                        list += this.template_contractors_li(this.options.contractors[li_item]);
                    }
                }
                $sidebar.find('ul.my-contractors-list', $sidebar).html(list);
            }

            uploader = new qq.FileUploaderBasic({
                button:this.$el.find('#file-uploader div')[0],
                action:'/grid/send/profile/logo',
                multiple:false,
                sizeLimit:1024 * 1024,
                onSubmit:function (id, fileName) {
                    thisView.$el.find('#avatar-logo').attr('src', thisView.currentAvatar);
                    thisView.$el.find('.logo-box').prepend(thisView.template_loader());
                    thisView.$el.find('.add-logo').css({visibility:'hidden'});
                },

                onComplete:function (a, b, c) {
                    if (c && c.success && c.imgUrl) {
                        thisView.$el.find('#avatar-logo').attr('src', c.imgUrl);
                        thisView.$el.find('a.add-logo').addClass('change-logo').removeClass('add-logo').text(thisView.locale.change_logo).css({visibility:'visible'});
                        thisView.$el.find('.logo-box').addClass('exist-logo').removeClass('empty-logo');
                        thisView.$el.find('.avatar-loader', thisView.$el).remove();
                    }
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

        ajaxAddPartnerRequest:function (data) {
            var that = this;

            function onSendAjaxSuccess(ajaxdata) {
                if (ajaxdata.error) {
                    Y.Informer.show('Ошибка добавления в контрагенты: ' + ajaxdata.msg, 10);
                } else {
                    Y.Modalbox.showSimple(data.action === 'add' ? 'Заявка успешно отправлена' : "Контрагент успешно добавлен");
                    $(data.eventObject.currentTarget).removeClass(data.removedClass).addClass(data.neededClass).text(data.newText);

                }
            }

            $.ajax(data.url, {
                success:onSendAjaxSuccess,
                error:function () {
                    Y.Informer.show(that.LG.messages.wrong.sending, 10);
                },
                type:'POST',
                data:data.post,
                dataType:'json',
                beforeSend:function (jqXHR) {
                    jqXHR.setRequestHeader("X-CSRFToken", Y.utils.getCookie('csrftoken'));
                }
            });
        }
    });

    SidebarView = Backbone.View.extend({
        modes_config:{
            'feedback':FeedbackSidebarView,
            'search':SearchSidebarView,
            'some_company':CompanyProfileSidebarView
        },

        currentMode:"",

        sidebarAction:function (linkId) {
            this.trigger('sidebarLinkClicked', linkId);
        },

        setMode:function (mode, data) {
            if (!this.modes_config.hasOwnProperty(mode)) {
                return;
            }

            this.currentMode = mode;
            var modeView = new this.modes_config[mode](data);
            modeView.bind('sidebarLinkClicked', this.sidebarAction, this);
            this.$el.empty().append(modeView.render().el);
            this.currentModeView = modeView;
        }
    });

    Y.MainSideBar = SidebarView;
}