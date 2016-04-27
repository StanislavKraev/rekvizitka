function x(Y) {
    "use strict";

    var PartnerManager, PartnerData, PartnerIncomingReq, PartnerOutgoingReq,
        default_list_logo = '/media/i/default_company_list.png';

    PartnerManager = Backbone.Model.extend({
        defaults : {
            rek_partners : null,
            incoming_requests : null,
            outgoing_requests : null,
            rek_partners_cancelled : null,
            incoming_requests_cancelled : null,
            outgoing_requests_cancelled : null,
            rek_id : '',
            brand_name : '',
            category_text : '',
            company_logo : default_list_logo,
            own : false,
            needReload : false,
            loadedFromInit : false
        },

        initialize : function() {
            this.cleanArrays();
            this.set('loadedFromInit', false);
        },

        loadPartnerData : function(callbackSuccess, callbackError) {
            var that = this;
            if(Y.Partners_init && Y.Partners_init.hasOwnProperty('rek_id') &&
                    Y.Partners_init.rek_id === this.get('rek_id')) {
                this.initMembers();
                callbackSuccess();
            } else {
                $.ajax('/' + this.get('rek_id') + '/contractors/i/', {
                    success : function(data) {
                        if(data.error) {
                            callbackError(data.error);
                        } else {
                            Y.Partners_init = data;
                            Y.Partners_init.rek_id = that.get('rek_id');
                            that.set('loadedFromInit', false);
                            that.initMembers();
                            callbackSuccess();
                        }
                    },
                    error : function(jqXHR, textStatus, errorThrown) {
                        callbackError(errorThrown);
                    },
                    type : 'GET',
                    dataType : 'json'
                });
            }
        },

        cleanArrays : function() {
            this.set('rek_partners', []);
            this.set('incoming_requests', []);
            this.set('outgoing_requests', []);
            this.set('rek_partners_cancelled', []);
            this.set('incoming_requests_cancelled', []);
            this.set('outgoing_requests_cancelled', []);
        },

        initMembers : function() {
            if(!this.get('loadedFromInit') || this.get('rek_id') !== Y.Partners_init.rek_id) {
                this.set('rek_partners', this.makePartnersArray(Y.Partners_init.rek_partners));
                this.set('incoming_requests', this.makeIncomingsArray(Y.Partners_init.incoming_requests));
                this.set('outgoing_requests', this.makeOutgoingsArray(Y.Partners_init.outgoing_requests));
                this.set('rek_id', Y.Partners_init.rek_id);
                this.set('brand_name', Y.Partners_init.brand_name);
                this.set('own', Y.Partners_init.own);
                this.set('company_logo', Y.Partners_init.company_logo);
                this.set('category_text', Y.Partners_init.category_text);
                this.set('needReload', false);
                this.set('loadedFromInit', true);
            }
        },

        makeObjectArray : function(serverArray, DataClass) {
            var result = [], i;
            for(i = 0; i < serverArray.length; i += 1) {
                result.push(new DataClass(serverArray[i]));
            }
            return result;
        },

        makePartnersArray : function(serverPartners) {
            return this.makeObjectArray(serverPartners, Y.PartnerData);
        },
        makeIncomingsArray : function(serverIncomings) {
            var incomings = this.makeObjectArray(serverIncomings, Y.PartnerIncomingReq);
            incomings.sort(function(obj1, obj2) {
                var compareResult = 0;
                if(obj1.get('viewed') !== obj2.get('viewed')) {
                    compareResult = (obj1.get('viewed') ? 1 : -1);
                } else {
                    compareResult = (obj1.get('brand_name') > obj2.get('brand_name') ? 1 : -1);
                }
                return compareResult;
            });
            return incomings;
        },
        makeOutgoingsArray : function(serverOutgoings) {
            return this.makeObjectArray(serverOutgoings, Y.PartnerOutgoingReq);
        },

        getArrayIndexByRekId : function(rekId, listname) {
            var i, result = null;
            for(i = 0; i < this.get(listname).length; i += 1) {
                if(this.get(listname)[i].get('rek_id') === rekId) {
                    result = i;
                    break;
                }
            }
            return result;
        },

        getElementByRekId : function(rekId, listname) {
            var i = this.getArrayIndexByRekId(rekId, listname), result = null;
            if(i !== null) {
                result = this.get(listname)[i];
            }
            return result;
        },

        moveRecordFromIncomingToMain : function(rekId) {
            var i = this.getArrayIndexByRekId(rekId, 'incoming_requests'), result = false;
            if(i !== null) {
                this.get('rek_partners').push(this.get('incoming_requests')[i]);
                this.get('incoming_requests').splice(i, 1);
                result = true;
                this.set('needReload', true);
            }
            return result;
        },

        deleteFromArray : function(rekId, listname) {
            var result = false, index = this.getArrayIndexByRekId(rekId, listname);
            if(index !== null) {
                this.get(listname + '_cancelled').push(this.get(listname).slice(index, 1)[0]);
                this.get(listname).splice(index, 1);
                result = true;
                this.set('needReload', true);
            }
            return result;
        },

        reviveFromCancelled : function(rekId, listname) {
            var result = false, cindex = this.getArrayIndexByRekId(rekId, listname + '_cancelled');
            if(cindex !== null) {
                this.get(listname).push(this.get(listname).slice(cindex, 1)[0]);
                this.get(listname + '_cancelled').splice(cindex, 1);
                result = true;
                this.set('needReload', true);
            }
            return result;
        },

        doesNeedReload : function() {
            return this.get('needReload');
        },

        getNonviewedIncomingCount : function() {
            var i, count = 0;
            for(i = 0; i < this.get('incoming_requests').length; i += 1) {
                if(!this.get('incoming_requests')[i].get('viewed')) {
                    count += 1;
                }
            }
            return count;
        }
    });

    PartnerData = Backbone.Model.extend({
        defaults : {
            rek_id : '',
            brand_name : '',
            logo : default_list_logo,
            kind_of_activity : '',
            employee_id : '',
            privacy : 'everyone'
        },

        initialize : function() {
            if(this.get('logo') === '') {
                this.set('logo', default_list_logo);
            }
        }
    });

    PartnerIncomingReq = Backbone.Model.extend({
        defaults : {
            rek_id : '',
            brand_name : '',
            logo : default_list_logo,
            employee_id : '',
            kind_of_activity : '',
            privacy : 'everyone',
            viewed : true
        },

        initialize : function() {
            if(this.get('logo') === '') {
                this.set('logo', default_list_logo);
            }
        }
    });

    PartnerOutgoingReq = Backbone.Model.extend({
        defaults : {
            rek_id : '',
            brand_name : '',
            logo : default_list_logo,
            employee_id : '',
            kind_of_activity : '',
            privacy : 'everyone'
        },

        initialize : function() {
            if(this.get('logo') === '') {
                this.set('logo', default_list_logo);
            }
        }
    });

    Y.PartnerManager = PartnerManager;
    Y.PartnerData = PartnerData;
    Y.PartnerIncomingReq = PartnerIncomingReq;
    Y.PartnerOutgoingReq = PartnerOutgoingReq;
}
