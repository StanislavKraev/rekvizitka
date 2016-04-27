# -*- coding: utf-8 -*-
from decimal import *
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import timezone
from django.views.generic.base import View
from django.core.paginator import Paginator

from rek.billing.models import Currency
from rek.promotions.models import Promotion, RegistrationPromoCode, create_reg_promotion
from rek.rekvizitka.models import Company

class AdsView(View):
    def get(self, request):
        return render_to_response('ads/aads_main.html', {}, context_instance=RequestContext(request))

class AddPromoActionView(View):
    def get(self, request):
        errors = {}
        action_data = {}
        return render_to_response('ads/add_promo_action.html', {'errors' : errors,
                                                                'action' : action_data},
            context_instance=RequestContext(request))

    def post(self, request):
        errors = {}
        if not request.POST.has_key('add_promo_action'):
            return HttpResponseBadRequest("Do not know what to do.")

        comment = request.POST.get('comment', '').strip()
        start_date = request.POST.get('start_date', '').strip()
        duration = request.POST.get('duration', '').strip()
        amount = request.POST.get('amount', '').strip()
        count = request.POST.get('count', '').strip()

        start_date_obj = None
        duration_int = 0
        amount_dec = Decimal(0)
        count_int = 0

        if not len(comment):
            errors['comment'] = 'Поле не может быть пустым'

        try:
            start_date_obj = datetime.strptime(start_date, '%d-%m-%Y')
        except Exception:
            errors['start_date'] = 'Некорректная дата'

        try:
            duration_int = int(duration)
            if duration_int <= 0:
                raise ValueError()
        except ValueError:
            errors['duration'] = 'Введите число > 0'

        try:
            count_int = int(count)
            if count_int <= 0 or count_int > 100000000:
                raise ValueError()
        except ValueError:
            errors['count'] = 'Введите число > 0'

        try:
            amount_dec = Decimal(amount)
            if amount_dec <= Decimal(0) or amount_dec > Decimal(1000000000):
                raise Exception()
        except Exception:
            errors['amount'] = 'Введите сумму в рублях.копейках (напр. 1000 или 10.22)'

        if not len(errors):
            create_reg_promotion(start_date_obj, duration_int, comment, Currency.russian_roubles(amount_dec), count_int)
            return HttpResponseRedirect('/ads/view_promo_actions/')

        return render_to_response('ads/add_promo_action.html', {'errors' : errors,
                                                                'comment' : comment,
                                                                'start_date' : start_date,
                                                                'duration' : duration,
                                                                'amount' : amount,
                                                                'count' : count},
                                  context_instance=RequestContext(request))

class ShowPromoActionsView(View):
    def get(self, request):
        actions = []
        promotions = Promotion.objects.get({})
        state_statuses = {
            Promotion.STATE_ACTIVE : 'активна',
            Promotion.STATE_DISABLED : 'заблокирована',
            }
        for promotion in promotions:
            codes = RegistrationPromoCode.objects.collection.find({'promotion_id' : promotion._id}).limit(3).sort([('used_date', -1)])
            actions.append({
                'comment' : promotion.comment,
                'id' : promotion._id,
                'status' : state_statuses[promotion.state],
                'start_date' : promotion.start_date.strftime('%d-%m-%Y'),
                'expires_date' : promotion.expires_date.strftime('%d-%m-%Y'),
                'codes' : codes,
                'type' : promotion.type
            })

        return render_to_response('ads/show_promo_actions.html',
            {'actions' : actions},
            context_instance=RequestContext(request))

class ShowPromoActionView(View):
    def get(self, request, action_id):
        try:
            action = Promotion.objects.get_one({'_id' : ObjectId(action_id)})
        except Exception:
            raise Http404()

        try:
            page = int(request.GET.get('page', 1))
        except Exception:
            page = 1

        state_statuses = {
            Promotion.STATE_ACTIVE : 'активна',
            Promotion.STATE_DISABLED : 'заблокирована',
        }

        action_data = {
            'comment' : action.comment,
            'creation_date' : action.creation_date,
            'start_date' : action.start_date,
            'expires_date' : action.expires_date,
            'status' : state_statuses.get(action.state, 'неизвестно'),
            'type' : action.type
        }

        reg_codes = RegistrationPromoCode.objects.get({'promotion_id' : action._id})
        reg_codes_list = [{'code' : code.code,
                           'company_id' : code.company_id,
                           'used_date' : code.used_date,
                           'price' : code.price} for code in reg_codes]

        p = Paginator(reg_codes_list, 10)
        try:
            reg_codes = p.page(page)
        except Exception:
            reg_codes = p.page(1)

        return render_to_response('ads/show_promo_action.html',
                                  {'action' : action_data,
                                   'reg_codes' : reg_codes},
                                  context_instance=RequestContext(request))

class ManagePromoActionView(View):
    def get(self, request, action_id):
        try:
            action = Promotion.objects.get_one({'_id' : ObjectId(action_id)})
        except Exception:
            raise Http404()

        action_data = {
            'comment' : action.comment,
            'start_date' : action.start_date.strftime('%d-%m-%Y'),
            'duration' : (action.expires_date - action.start_date).days,
            'state' : action.state,
            'type' : action.type,
            'id' : unicode(action._id)
        }

        return render_to_response('ads/manage_promo_action.html',
                {'action' : action_data},
            context_instance=RequestContext(request))

    def post(self, request, action_id):
        try:
            action = Promotion.objects.get_one({'_id' : ObjectId(action_id)})
        except Exception:
            raise Http404()

        errors = {}
        comment = ""
        start_date = ""
        duration_int = 0

        if request.POST.has_key('disable_promo_action'):
            if action.state == Promotion.STATE_ACTIVE:
                Promotion.objects.update({'_id' : action._id}, {'$set' : {'state' : Promotion.STATE_DISABLED}})
                return HttpResponseRedirect('/ads/view_promo_actions/%s/' % action_id)
            else:
                errors['general'] = 'Невозможно заблокировать акцию: уже заблокирована.<br>'
        elif request.POST.has_key('enable_promo_action'):
            if action.state != Promotion.STATE_ACTIVE:
                Promotion.objects.update({'_id' : action._id}, {'$set' : {'state' : Promotion.STATE_ACTIVE}})
                return HttpResponseRedirect('/ads/view_promo_actions/%s/' % action_id)
            else:
                errors['general'] = 'Невозможно активировать акцию: уже активна.<br>'
        else:
            comment = request.POST.get('comment', '').strip()
            start_date = request.POST.get('start_date', '').strip()
            duration = request.POST.get('duration', '').strip()

            start_date_obj = None
            duration_int = 0

            if not len(comment):
                errors['comment'] = 'Поле не может быть пустым'

            try:
                start_date_obj = datetime.strptime(start_date, '%d-%m-%Y')
            except Exception:
                errors['start_date'] = 'Некорректная дата'

            try:
                duration_int = int(duration)
                if duration_int <= 0:
                    raise ValueError()
            except ValueError:
                errors['duration'] = 'Введите число > 0'

            if not len(errors):
                Promotion.objects.update({'_id' : action._id},
                                         {'$set' : {
                        'comment' : comment,
                        'start_date' : start_date_obj,
                        'expires_date' : start_date_obj + timedelta(days=duration_int)
                    }})
                return HttpResponseRedirect('/ads/view_promo_actions/%s/' % action_id)

        action_data = {
            'comment' : comment,
            'start_date' : start_date,
            'duration' : duration_int,
            'state' : action.state,
            'type' : action.type,
            'id' : unicode(action._id)
        }
        return render_to_response('ads/manage_promo_action.html',
                {'action' : action_data,
                 'errors' : errors},
            context_instance=RequestContext(request))

class ManagePromoCodeView(View):
    def get(self, request, promo_id):
        try:
            code = RegistrationPromoCode.objects.get_one({'code' : int(promo_id)})
            if not code:
                raise Exception()
        except Exception:
            raise Http404()

        promo_action = Promotion.objects.get_one({'_id' : code.promotion_id})
        code_data = {
            'code' : code.code,
            'price' : code.price,
            'used_date' : code.used_date,
            'company_id' : code.company_id,
            'company' : Company.objects.get_one({'_id' : code.company_id}) if code.company_id else "--------",
            'promo_action' : promo_action,
            'promo_action_url' : '/ads/view_promo_actions/%s/' % promo_action._id
        }

        return render_to_response('ads/manage_promo_code.html',
                {'code' : code_data},
            context_instance=RequestContext(request))

    def post(self, request, promo_id):
        try:
            code = RegistrationPromoCode.objects.get_one({'code' : int(promo_id)})
            if not code:
                raise Exception()
        except Exception:
            raise Http404()

        if request.POST.has_key('clear_promo_code'):
            if code.used_date is not None:
                code.used_date = None
                code.company_id = None
                code.save()
        elif request.POST.has_key('use_promo_code'):
            if code.used_date is None:
                code.used_date = timezone.now()
                code.company_id = None
                code.save()

        return HttpResponseRedirect('/ads/promo_code/%s/' % code.code)