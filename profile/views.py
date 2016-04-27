# -*- coding: utf-8 -*-

from datetime import datetime
import os

from django.utils import timezone
from django.contrib.auth import authenticate as auth_authenticate
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from django.utils.html import escape
from django.views.generic.base import  View
from rek.mango.auth import get_password_error

from rek.mongo.conn_manager import mongodb_connection_manager
from rek.rekvizitka.models import StaffSizeEnum, CompanyCategoryEnum, get_categories_list
from rek.rekvizitka.permissions import  CompanyPermission
from rek.rekvizitka.models import Company

def get_pisa_name(full_path):
    base, file_name = os.path.split(full_path)
    file, ext = os.path.splitext(file_name)
    return os.path.join(base, u"pisa_%s.jpeg" % file)

def is_dict_empty(dict_obj, keys):
    for key in keys:
        if key in dict_obj and len(unicode(dict_obj[key]).strip()):
            return False
    return True

class PostPreparator(object):
    def __init__(self, dict_obj):
        self.dict_obj = dict_obj

    def __call__(self, field, default_value=None):
        return unicode(self.dict_obj.get(field, default_value)).strip()

class EditProfileView(View):
    BUFFER_SIZE = 1024 * 128
    LOGO_MAX_SIZE = 1024 * 512
    SUPPORTED_IMAGE_EXTS = ('.PNG', '.GIF', '.BMP', '.JPG', '.JPEG', '.PCX', '.TIFF', '.TIF')
    DESCRIPTION_MAX_LENGTH = 1000

    profile_files_collection = mongodb_connection_manager.database['company_profile_files.files']

    def post(self, request):
        if not request.user or not request.user.is_authenticated():
            raise Http404()

        company = request.company

        check = CompanyPermission(request.user, request.employee, company)
        if not check.can_modify(company):
            return HttpResponseForbidden()

        if not request.is_ajax():
            return HttpResponseForbidden()

        if 'act' not in request.POST:
            raise Http404

        action = request.POST['act']

        if action == 'cnt':
            return self.process_contacts(company, request)
        elif action == 'gi':
            return self.process_general_info(company, request)
        elif action == 'set':
            return self.process_settings(company, request)

        raise Http404()

    def get_map_img(self, image_id, rek_id):
        if image_id and len(image_id):
            img = self.profile_files_collection.find_one({'rek_id' : rek_id, 'filename' : image_id})
            if img:
                return {'dim' : (img['width'], img['height']), 'filename' : image_id}
        return {'dim' : (0, 0), 'filename' : ''}

    def process_contacts(self, company, request):
        if 'data' not in request.POST:
            raise Http404()

        try:
            data = simplejson.loads(request.POST['data'])
        except Exception:
            raise Http404()

        update_data = {}

        if 'main_phone' in data:
            update_data['phones'] = [(data['main_phone'] or "").strip()]
            data['main_phone'] = update_data['phones'][0]

        if 'main_email' in data:
            update_data['emails'] = [(data['main_email'] or "").strip()]
            data['main_email'] = update_data['emails'][0]

        if 'main_site' in data:
            web_site = (data['main_site'] or "").strip().lower()
            if len(web_site) and web_site.find('://') == -1:
                root_web_addr = "http://" + web_site
            else:
                root_web_addr = web_site
            update_data['web_sites'] = [root_web_addr]
            data['main_site'] = update_data['web_sites'][0]

        if 'offices' in data and hasattr(data['offices'], '__iter__'):
            offices = []
            update_data['offices'] = offices
            for office in data['offices']:
                try:
                    offices.append({
                        'city' : (office.get('city', "")).strip(),
                        'information' : (office.get('information', "")).strip(),
                        'map_img' : self.get_map_img(office.get('imgID', ""), company.rek_id),
                        'imgID' : office.get('imgID', "")
                    })
                except Exception:
                    pass

            data['offices'] = []
            for office in offices:
                img = office['map_img']
                data['offices'].append({
                    'city' : office['city'],
                    'information' : office['information'],
                    'img_src' : '/grid/profile/%s/%s.jpg' % (company.rek_id, img['filename']) if img['filename'] and len(img['filename']) else "",
                    'img_width' : img['dim'][0],
                    'img_height' : img['dim'][1],
                    'imgID' : office['imgID']
                })

        if len(update_data.keys()):
            Company.objects.update({'_id' : company._id}, {'$set' : update_data})

        result = { 'success': True, 'data' : data }
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

    def process_settings(self, company, request):
        if 'data' not in request.POST:
            raise Http404()

        try:
            data = simplejson.loads(request.POST['data'])
        except Exception:
            raise Http404()

        update_data = {}

        if len(update_data.keys()):
            #Company.objects.update({'_id' : company._id}, {'$set' : update_data})
            pass

        result = { 'success': True, 'data' : data }
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

    def process_description(self, company, request):
        if 'descr' not in request.POST:
            raise Http404()

        new_description = request.POST['descr']
        if not len(new_description):
            return HttpResponse(simplejson.dumps({'success': False}), mimetype='application/javascript')
        if len(new_description) > self.DESCRIPTION_MAX_LENGTH:
            new_description = new_description[:self.DESCRIPTION_MAX_LENGTH]
        company.description = escape(new_description)
        company.save()

        result = { 'success': True, 'val' : new_description }
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

    def process_remove_avatar(self, request):
        employee = request.user.get_profile()
        if not employee:
            return HttpResponse(simplejson.dumps({ 'success': False }), mimetype='application/javascript')

        if employee.avatar:
            #noinspection PyUnresolvedReferences
            file_name = employee.avatar.path
            if os.path.exists(file_name):
                try:
                    os.remove(file_name)
                except Exception:
                    pass
            employee.avatar = None
            employee.save()

        result = { 'success': True }
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

    def process_accounts(self, company, request):
        for key, val in request.POST.iteritems():
            if key.startswith('account_cb'):
                try:
                    account_id = int(key[10:])
                    if account_id < 1:
                        continue
                    account = company.account_set.get(id=account_id)
                    account.hidden = val == "true"
                    account.save()
                except Exception:
                    continue

        result = { 'success': True }
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

    def process_general_info(self, company, request):
        if 'data' not in request.POST:
            raise Http404()

        try:
            data = simplejson.loads(request.POST['data'])
        except Exception:
            raise Http404()

        postPrep = PostPreparator(data)

        if 'brandName' in data:
            brand_name = postPrep('brandName')
            if not len(brand_name):
                return HttpResponse(simplejson.dumps({'success': False}), mimetype='application/javascript')

            company.brand_name = brand_name

        if 'descr' in data:
            descr = postPrep('descr')
            company.description = descr

        if 'shortName' in data:
            short_name = postPrep('shortName')
            company.short_name = short_name

        if 'fullName' in data:
            full_name = postPrep('fullName')
            company.full_name = full_name

        if 'categoryText' in data:
            category_text = postPrep('categoryText')
            company.category_text = category_text

        if 'genDir' in data:
            gen_dir = postPrep('genDir')
            company.gen_director = gen_dir

        if 'genAcc' in data:
            gen_acc = postPrep('genAcc')
            company.chief_accountant = gen_acc

        if 'estYear' in data:
            est_year = postPrep('estYear')
            try:
                est_year_i = int(est_year)
            except ValueError:
                est_year_i = 0

            if est_year_i < 1800 or est_year_i > timezone.now().year + 1:
                company.date_established = None
            else:
                company.date_established = datetime(year=est_year_i, month=1, day=1)

        if 'staffSize' in data:
            try:
                staff_size_i = int(postPrep('staffSize'))
            except ValueError:
                staff_size_i = StaffSizeEnum.UNKNOWN
            if not staff_size_i in StaffSizeEnum.ALL or staff_size_i == StaffSizeEnum.UNKNOWN:
                staff_size_i = StaffSizeEnum.UNKNOWN
            company.staff_size = staff_size_i

        if 'inn' in data:
            inn = postPrep('inn')
            try:
                inn_i = int(inn)
            except ValueError:
                inn_i = None
            company.inn = inn_i

        if 'kpp' in data:
            kpp = postPrep('kpp')
            try:
                kpp_i = int(kpp)
            except ValueError:
                kpp_i = None
            company.kpp = kpp_i

        bank_account = None
        if 'bank_account' in data:
            account_dict = data['bank_account']
            postPrepBank = PostPreparator(account_dict)
            bank_account = {'bank' : postPrepBank('bank', ''),
                            'bank_address' : postPrepBank('bank_address', ''),
                            'bik' : postPrepBank('bik', ''),
                            'correspondent_account' : postPrepBank('correspondent_account', ''),
                            'settlement_account' : postPrepBank('settlement_account', ''),
                            'recipient' : postPrepBank('recipient', '')}
            company.bank_accounts = [bank_account]

        if 'categories' in data:
            new_cat_list = [cat for cat in data['categories'] if cat and isinstance(cat, basestring) and cat in CompanyCategoryEnum.ALL]
            company.categories = new_cat_list

        company.save()
        data = {
            'brandName' : company.brand_name,
            'descr' : company.description or '',
            'shortName' : company.short_name or '',
            'fullName' : company.full_name or '',
            'inn' : unicode(company.inn) if company.inn else '',
            'kpp' : unicode(company.kpp) if company.kpp else '',
            'categoryText' : company.category_text or '',
            'genDir' : company.gen_director or '',
            'genAcc' : company.chief_accountant or '',
            'estYear' : company.date_established.year if company.date_established else '',
            'staffSize' : company.staff_size or StaffSizeEnum.UNKNOWN,
            'bank_account' : bank_account or {
                'bank' : "",
                'bank_address' : "",
                'bik' : "",
                'correspondent_account' : "",
                'settlement_account' : "",
                'recipient' : ""
            },
            'categories' : get_categories_list(company)
        }

        result = { 'success': True, 'data' : data }
        result_json = simplejson.dumps(result)
        return HttpResponse(result_json, mimetype='application/javascript')

class ChangePasswordView(View):
    def post(self, request):
        old_password = request.POST.get('old', '')
        new_password = request.POST.get('new', '')
        new_repeat_password = request.POST.get('new2', '')

        old_pwd_error = get_password_error(old_password)
        if old_pwd_error:
            return HttpResponse(simplejson.dumps({'error' : True, 'loc' : 'old', 'msg' : old_pwd_error}), mimetype='application/javascript')

        auth_user = auth_authenticate(username=self.request.user.email, password=old_password)
        if not auth_user:
            return HttpResponse(simplejson.dumps({'error' : True, 'loc' : 'old', 'msg' : u"Введен неправильный старый пароль"}), mimetype='application/javascript')

        new_pwd_error = get_password_error(new_password)
        if new_pwd_error:
            return HttpResponse(simplejson.dumps({'error' : True, 'loc' : 'new', 'msg' : new_pwd_error}), mimetype='application/javascript')

        if new_password != new_repeat_password:
            return HttpResponse(simplejson.dumps({'error' : True, 'loc' : 'new2', 'msg' : u"Введенные пароли не совпадают"}), mimetype='application/javascript')

        if new_password == old_password:
            return HttpResponse(simplejson.dumps({'error' : True, 'loc' : 'new', 'msg' : u"Старый и новый пароли одинаковые"}), mimetype='application/javascript')

        self.request.user.set_password(new_password)
        self.request.user.save()
        return HttpResponse(simplejson.dumps({}), mimetype='application/javascript')
