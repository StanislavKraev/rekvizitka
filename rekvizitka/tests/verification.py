# -*- coding: utf-8 -*-
import bson
import datetime
from django.core import mail
from django.utils import simplejson, timezone

from rek.billing.models import Invoice, InvoiceStatusEnum
from rek.deferred_notification.actions import RECOMMENDATION_ASKED, create_action_id
from rek.deferred_notification.models import Notification
from rek.invites.models import RecommendationRequest, RecommendationStatusEnum, Invite
from rek.invites.views import RecommendInitialsView
from rek.mango.auth import User
from rek.rekvizitka.account_statuses import CompanyAccountStatus
from rek.rekvizitka.models import CompanyEmployee, Company
from rek.rekvizitka.utils import integer_to_code

from rek.system_data.rek_settings import SettingsManager
from rek.tests.base import BaseTestCase

# mustdo: mails -> deferred notifications

class VerificationTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees',
                        'sessions', 'bill_items', 'recommendation_requests',
                        'deferred_notifications', 'user_activation_links', 'billing_accounts',
                        'invites']

    def placeBill(self):
        rekvizitka_bank_account = {
            'recipient' : u'ООО "РЕК1.РУ"',
            'address' : u'192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
            'account' : u'30101810000000000201',
            'account_name' : u'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',
            'bank_name' : u'ОАО АКБ "Авангард" г.Москва',
            'bank_bik' : 044525201,
            'bank_account' : u'40702810802890008194',
            }

        bill_data = {
            'payer' : self.company._id,
            'number' : u'КЦ-111',
            'position' : u'Верификация в информационной системе',
            'status' : 0,
            'duration_days':30,
            'price' : 1000000
        }
        bill_data.update(rekvizitka_bank_account)
        bill = Invoice(bill_data)
        bill.save()
        return bill

    def placeExpiredBill(self):
        rekvizitka_bank_account = {
            'recipient' : u'ООО "РЕК1.РУ"',
            'address' : u'192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
            'account' : u'30101810000000000201',
            'account_name' : u'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',
            'bank_name' : u'ОАО АКБ "Авангард" г.Москва',
            'bank_bik' : 044525201,
            'bank_account' : u'40702810802890008194',
            }

        bill_data = {
            'payer' : {'_id' : self.company._id},
            'number' : u'КЦ-111',
            'position' : u'Верификация в информационной системе',
            'status' : InvoiceStatusEnum.EXPIRED,
            'duration_days':30,
            'price' : 1000000,
            'create_date' : datetime.datetime(2011, 1, 1),
            'expire_date' : datetime.datetime(2011, 1, 1) + datetime.timedelta(days=30)
        }
        bill_data.update(rekvizitka_bank_account)
        id = Invoice.objects.collection.insert(bill_data)
        return Invoice.objects.get_one({'_id' : id})

    def register_verification_requesters(self, target_company, count = 10, status = RecommendationStatusEnum.RECEIVED):
        requesters = []
        for a in xrange(count):
            user = User.create_user('requester_user%d@testdomain.xy' % a, 'aaa')
            User.collection.update({'_id' : user._id}, {'$set' : {'activated' : True}})
            if not user:
                raise Exception('failed to create test user')

            employee = CompanyEmployee({'user_id' : user._id,
                                        'first_name' : 'test_user_' + str(a)})
            employee.save()
            company = Company({'rek_id' : integer_to_code(a + 10000),
                               'owner_employee_id' : employee._id,
                               'short_name' : 'tc_' + str(a),
                               'full_name' : 'OOO Test Company ' + str(a),
                               'brand_name' : 'Test Company Brand ' + str(a),
                               'description' : 'Test company ' + str(a),
                               'category_text' : 'Testing',
                               'staff_size' : (a + 1) * 3,
                               'inn' : int(str(a + 1) + '0' * (12 - len(str(a)))) + a + 1,
                               'kpp' : int(str(a + 1) + '1' * (9 - len(str(a)))) + a + 1,
                               'account_status' : CompanyAccountStatus.JUST_REGISTERED,
                               'is_account_activated' : True
            })
            company.save()
            employee.set(company_id = company._id)

            request = RecommendationRequest({'requester' : company._id,
                                             'recipient' : target_company._id,
                                             'status' : status,
                                             'message' : 'Please recommend me.',
                                             'requester_email' : user.email})
            request.save()

            requesters.append((company, employee, user, request))
        return requesters

    def testShowVerifyPageUnverified(self):
        self.register(verified=False)
        self.login()
        response = self.client.get('/verification/')
        self.assertEqual(response.status_code, 200)

    def testShowVerifyPageVerified(self):
        self.register()
        self.login()
        response = self.client.get('/verification/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'][17:], '/')

    def testPlaceABill(self):
        self.register(verified=False)
        self.login()
        response = self.client.get('/verification/place_bill/')
        self.assertEqual(response.status_code, 405)
        response = self.client.post('/verification/place_bill/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.collections['bill_items'].count(), 1)
        bill = self.collections['bill_items'].find_one()
        self.assertIsNotNone(bill)
        self.assertIn('_id', bill)
        self.assertEqual(bill['price'], SettingsManager.get_property('verify_bill_price'))

    def testPlaceSecondBill(self):
        self.register(verified=False)
        self.login()
        response = self.client.post('/verification/place_bill/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.collections['bill_items'].count(), 1)
        bill = self.collections['bill_items'].find_one()
        self.assertIsNotNone(bill)
        self.assertIn('_id', bill)
        self.assertEqual(bill['price'], SettingsManager.get_property('verify_bill_price'))

        response = self.client.post('/verification/place_bill/')
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('error', data)
        self.assertTrue(data['error'])

    def testPrintBillNotCreated(self):
        self.register(verified=False)
        self.login()
        bill_id = bson.ObjectId()
        response = self.client.get('/get/%(bill_id)s/bill.html' % {'bill_id' : str(bill_id)})
        self.assertEqual(response.status_code, 404)

    def testPrintBillCreated(self):
        self.register(verified=False)
        self.login()
        bill = self.placeBill()
        response = self.client.get('/get/%(bill_id)s/bill.html' % {'bill_id' : str(bill._id)})
        self.assertEqual(response.status_code, 200)

        self.assertIn('recipient', response.context)
        self.assertIn('bill', response.context)
        self.assertIn('payer', response.context)

    def testGetPdfNotCreated(self):
        self.register(verified=False)
        self.login()
        bill_id = bson.ObjectId()
        response = self.client.get('/get/%(bill_id)s/bill.pdf' % {'bill_id' : str(bill_id)})
        self.assertEqual(response.status_code, 404)

    def testGetPdfCreated(self):
        self.register(verified=False)
        self.login()
        bill = self.placeBill()
        response = self.client.get('/get/%(bill_id)s/bill.pdf' % {'bill_id' : str(bill._id)})
        self.assertEqual(response.status_code, 200)

        self.assertIn('recipient', response.context)
        self.assertIn('bill', response.context)
        self.assertIn('payer', response.context)

    def testSendEmailNotCreated(self):
        self.register(verified=False)
        self.login()
        mail.outbox = []
        bill_id = bson.ObjectId()
        response = self.client.post('/send_verify_bill/', {'bill_id' : str(bill_id)})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], True)
        self.assertEqual(len(mail.outbox), 0)

    def testSendEmailCreated(self):
        self.register(verified=False)
        self.login()
        mail.outbox = []
        bill = self.placeBill()
        response = self.client.post('/send_verify_bill/', {'bill_id' : str(bill._id)})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], False)
        self.assertEqual(len(mail.outbox), 1)

    def testPlaceABillNotAuthorized(self):
        self.register(verified=False)
        response = self.client.post('/verification/place_bill/')
        self.assertEqual(response.status_code, 302)

    def testShowBillNotAuthorized(self):
        self.register(verified=False)
        self.placeBill()
        response = self.client.get('/verification/')
        self.assertEqual(response.status_code, 302)

    def testPrintExpiredBill(self):
        self.register(verified=False)
        self.login()
        bill = self.placeExpiredBill()
        self.assertEqual(bill.status, InvoiceStatusEnum.EXPIRED)
        response = self.client.get('/get/%(bill_id)s/bill.html' % {'bill_id' : str(bill._id)})
        self.assertEqual(response.status_code, 404)
        found_bill_data = Invoice.objects.collection.find_one({'_id' : bill._id})
        self.assertIsNotNone(found_bill_data)
        self.assertEqual(found_bill_data['status'], InvoiceStatusEnum.EXPIRED)

    def testSendEmailExpiredBill(self):
        self.register(verified=False)
        self.login()
        mail.outbox = []
        bill = self.placeExpiredBill()
        response = self.client.post('/send_verify_bill/', {'bill_id' : str(bill._id)})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], True)
        found_bill_data = Invoice.objects.collection.find_one({'_id' : bill._id})
        self.assertIsNotNone(found_bill_data)
        self.assertEqual(found_bill_data['status'], InvoiceStatusEnum.EXPIRED)
        self.assertEqual(len(mail.outbox), 0)

    def testSearchEmptyString(self):
        self.register_companies()
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/0', {'q' : ''})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)

        response = self.client.get('/verify/c/0')
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)

    def testSearchShortName(self):
        self.register_companies(12)
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/0', {'q' : 'tc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 10)

        response = self.client.get('/verify/c/1', {'q' : 'tc_0'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 1)

        response = self.client.get('/verify/c/1', {'q' : 'tc_not_created'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 0)

    def testSearchReturnData(self):
        companies = self.register_companies(3)
        company = companies[1]
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/1', {'q' : company.short_name})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 1)
        item = data['companies'][0]
        self.assertEquals(item['code'], company.rek_id)
        self.assertEquals(item['name'], company.brand_name)
        self.assertEquals(item['kind_of_activity'], company.category_text)
        self.assertEquals(item['send_status'], False)

        self.assertEquals(data['pages'], 1)
        self.assertEquals(data['page'], 1)
        self.assertEquals(data['can_send'], True)

    def testSearchPaging(self):
        self.register_companies(53)
        self.register(verified=False)
        self.login()

        response = self.client.get('/verify/c/1', {'q' : 'tc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 10)

        self.assertEquals(data['pages'], 6)
        self.assertEquals(data['page'], 1)
        self.assertEquals(data['can_send'], True)

        response = self.client.get('/verify/c/3', {'q' : 'tc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 10)

        self.assertEquals(data['pages'], 6)
        self.assertEquals(data['page'], 3)

        response = self.client.get('/verify/c/f', {'q' : 'tc'})
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/verify/c/6', {'q' : 'tc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 3)

        self.assertEquals(data['pages'], 6)
        self.assertEquals(data['page'], 6)

        response = self.client.get('/verify/c/-1', {'q' : 'tc'})
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/verify/c/6', {'q' : 'tc'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 3)

        response = self.client.get('/verify/c/1', {'q' : 'tc_1'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 10)

        self.assertEquals(data['pages'], 2)
        self.assertEquals(data['page'], 1)

    def testSearchFullName(self):
        self.register_companies(12)
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/1', {'q' : 'OOO Test Company'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 10)
        self.assertEquals(data['pages'], 2)
        self.assertEquals(data['page'], 1)

    def testSearchBrandName(self):
        self.register_companies(22)
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/2', {'q' : 'Test Company Brand'})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 10)
        self.assertEquals(data['pages'], 3)
        self.assertEquals(data['page'], 2)

    def testSearchRekId(self):
        companies = self.register_companies(3)
        rek_id = companies[0].rek_id
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/1', {'q' : rek_id})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 1)
        self.assertEquals(data['pages'], 1)
        self.assertEquals(data['page'], 1)

    def testSearchInn(self):
        companies = self.register_companies(3)
        inn = companies[0].inn
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/1', {'q' : str(inn)})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 1)
        self.assertEquals(data['pages'], 1)
        self.assertEquals(data['page'], 1)

        response = self.client.get('/verify/c/1', {'q' : str(inn + 9999)})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 0)

    def testSearchKpp(self):
        companies = self.register_companies(3)
        kpp = companies[0].kpp
        self.register(verified=False)
        self.login()
        response = self.client.get('/verify/c/1', {'q' : str(kpp)})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 1)
        self.assertEquals(data['pages'], 1)
        self.assertEquals(data['page'], 1)

        response = self.client.get('/verify/c/1', {'q' : str(kpp + 9999)})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('companies', data)
        self.assertEqual(len(data['companies']), 0)

    def testSearchUnauthorized(self):
        self.register_companies(12)
        self.register(verified=False)
        response = self.client.get('/verify/c/1', {'q' : 'tc'})
        self.assertEqual(response.status_code, 302)

    def testRequestRecommendation(self):
        message = "Could you please recommend me."
        self.register(verified=False)
        self.login()
        mail.outbox = []
        companies = self.register_companies(3)
        requested_company = companies[0]
        rek_id = requested_company.rek_id
        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : rek_id})
        self.assertEqual(response.status_code, 400) # no required parameter 'message'

        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : rek_id}, {'message' : message})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(RecommendationRequest.objects.count(), 1)

        recommendation = RecommendationRequest.objects.get({})[0]
        self.assertEqual(recommendation.requester, self.company._id)
        self.assertEqual(recommendation.recipient, requested_company._id)
        self.assertEqual(recommendation.message, message)
        self.assertEqual(recommendation.status, RecommendationStatusEnum.RECEIVED)
        self.assertEqual(recommendation.viewed, False)
        self.assertTrue(timezone.now() - datetime.timedelta(seconds=10) < recommendation.send_date < timezone.now())

        self.assertIsNotNone(recommendation)
        action = create_action_id(RECOMMENDATION_ASKED, recommendation._id)
        notification = Notification.objects.get_one({'action' : action})
        self.assertIsNotNone(notification)

    def testRequestMaxNumOfRecs(self):
        SettingsManager.set_property('rnes', 3)
        SettingsManager.set_property('rmax', 3)
        message = "Could you please recommend me."
        self.register(verified=False)
        self.login()
        companies = self.register_companies(6)

        for x in xrange(3):
            company = companies[x]
            response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : company.rek_id}, {'message' : message})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(RecommendationRequest.objects.count(), x + 1)

        company = companies[-1]
        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : company.rek_id}, {'message' : message})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(RecommendationRequest.objects.count(), 3)

    def testRequestRecUnauthorized(self):
        message = "Could you please recommend me."
        self.register(verified=False)

        companies = self.register_companies(3)
        requested_company = companies[0]
        rek_id = requested_company.rek_id

        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : rek_id}, {'message' : message})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RecommendationRequest.objects.count(), 0)

    def testRequestRecToUnavailableCompany(self):
        message = "Could you please recommend me."
        self.register(verified=False)
        self.login()

        companies = self.register_companies(3)
        requested_company = companies[0]
        rek_id = requested_company.rek_id

        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : rek_id + 'CCC'}, {'message' : message})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(RecommendationRequest.objects.count(), 0)

    def testAcceptRec(self):
        SettingsManager.set_property('rnes', 3)
        self.register()
        requester_company, requester_employee, requester_user, request = self.register_verification_requesters(self.company, 3)[0]

        self.login()
        mail.outbox = []

        self.assertEqual(RecommendationRequest.objects.count(), 3)

        response = self.client.post('/recommendations/accept/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('error', data)
        self.assertFalse(data['error'])

        self.assertEqual(len(mail.outbox), 0)

        request_post = RecommendationRequest.objects.get_one({'_id' : request._id})
        self.assertIsNotNone(request_post)
        self.assertEqual(request_post.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(request_post.requester, requester_company._id)
        self.assertEqual(request_post.recipient, self.company._id)
        self.assertEqual(request_post.viewed, False)
        self.assertEqual(request_post.requester_email, requester_user.email)

        self.assertEqual(RecommendationRequest.objects.count(), 3)

    def testAcceptRecAndVerify(self):
        SettingsManager.set_property('rnes', 3)
        self.register()
        requesters = self.register_verification_requesters(self.company, 1)
        requester_company, requester_employee, requester_user, request = requesters[0]

        self.login()
        mail.outbox = []

        response = self.client.post('/recommendations/accept/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        company_data = Company.objects.collection.find_one({'_id' : requester_company._id}, {'account_status' : 1})
        self.assertEqual(company_data['account_status'], CompanyAccountStatus.JUST_REGISTERED)

        self.logout()
        self.register(email='registered1@testunavailabledomain.ru')
        request = RecommendationRequest({'requester' : requester_company._id,
                                         'recipient' : self.company._id,
                                         'status' : RecommendationStatusEnum.RECEIVED,
                                         'message' : 'Please recommend me.',
                                         'requester_email' : 'kraevst@yandexyandexyandex.ru'})
        request.save()

        self.login_as(email='registered1@testunavailabledomain.ru')

        mail.outbox = []

        response = self.client.post('/recommendations/accept/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        company_data = Company.objects.collection.find_one({'_id' : requester_company._id}, {'account_status' : 1})
        self.assertEqual(company_data['account_status'], CompanyAccountStatus.JUST_REGISTERED)

        self.logout()
        self.register(email='registered2@testunavailabledomain.ru')
        request = RecommendationRequest({'requester' : requester_company._id,
                                         'recipient' : self.company._id,
                                         'status' : RecommendationStatusEnum.RECEIVED,
                                         'message' : 'Please recommend me.',
                                         'requester_email' : 'kraevst@yandexyandexyandex.ru'})
        request.save()

        self.login_as(email='registered2@testunavailabledomain.ru')

        mail.outbox = []

        response = self.client.post('/recommendations/accept/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        company_data = Company.objects.collection.find_one({'_id' : requester_company._id}, {'account_status' : 1})
        self.assertEqual(company_data['account_status'], CompanyAccountStatus.VERIFIED)

    def testAcceptAccepted(self):
        self.register()
        requester_company, requester_employee, requester_user, request = self.register_verification_requesters(self.company, 3, status=RecommendationStatusEnum.ACCEPTED)[0]

        self.login()
        mail.outbox = []

        self.assertEqual(RecommendationRequest.objects.count(), 3)

        response = self.client.post('/recommendations/accept/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('error', data)
        self.assertTrue(data['error'])

        self.assertEqual(len(mail.outbox), 0)

        request_post = RecommendationRequest.objects.get_one({'_id' : request._id})
        self.assertIsNotNone(request_post)
        self.assertEqual(request_post.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(request_post.requester, requester_company._id)
        self.assertEqual(request_post.recipient, self.company._id)
        self.assertEqual(request_post.viewed, False)
        self.assertEqual(request_post.requester_email, requester_user.email)

        self.assertEqual(RecommendationRequest.objects.count(), 3)

    def testRejectRec(self):
        self.register()
        requester_company, requester_employee, requester_user, request = self.register_verification_requesters(self.company, 3)[0]

        self.login()
        mail.outbox = []

        self.assertEqual(RecommendationRequest.objects.count(), 3)

        response = self.client.post('/recommendations/decline/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('error', data)
        self.assertFalse(data['error'])

        self.assertEqual(len(mail.outbox), 0)

        request_post = RecommendationRequest.objects.get_one({'_id' : request._id})
        self.assertIsNotNone(request_post)
        self.assertEqual(request_post.status, RecommendationStatusEnum.DECLINED)
        self.assertEqual(request_post.requester, requester_company._id)
        self.assertEqual(request_post.recipient, self.company._id)
        self.assertEqual(request_post.viewed, False)
        self.assertEqual(request_post.requester_email, requester_user.email)

        self.assertEqual(RecommendationRequest.objects.count(), 3)

    def testRejectRejected(self):
        self.register()
        requester_company, requester_employee, requester_user, request = self.register_verification_requesters(self.company, 3, status=RecommendationStatusEnum.DECLINED)[0]

        self.login()
        mail.outbox = []

        self.assertEqual(RecommendationRequest.objects.count(), 3)

        response = self.client.post('/recommendations/decline/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('error', data)
        self.assertTrue(data['error'])

        self.assertEqual(len(mail.outbox), 0)

        request_post = RecommendationRequest.objects.get_one({'_id' : request._id})
        self.assertIsNotNone(request_post)
        self.assertEqual(request_post.status, RecommendationStatusEnum.DECLINED)
        self.assertEqual(request_post.requester, requester_company._id)
        self.assertEqual(request_post.recipient, self.company._id)
        self.assertEqual(request_post.viewed, False)
        self.assertEqual(request_post.requester_email, requester_user.email)

        self.assertEqual(RecommendationRequest.objects.count(), 3)

    def testInitialModuleDataAccept(self):
        SettingsManager.set_property('rnes', 3)
        self.register()
        requesters = self.register_verification_requesters(self.company, 3)
        requester_company, requester_employee, requester_user, request = requesters[0]

        self.login()
        mail.outbox = []

        self.assertEqual(RecommendationRequest.objects.count(), 3)

        response = self.client.post('/recommendations/accept/%s/' % str(request._id))
        self.assertEqual(response.status_code, 200)

        data = simplejson.loads(response.content)
        self.assertTrue(isinstance(data, dict))
        self.assertIn('error', data)
        self.assertFalse(data['error'])

        self.assertEqual(len(mail.outbox), 0)

        request_post = RecommendationRequest.objects.get_one({'_id' : request._id})
        self.assertIsNotNone(request_post)
        self.assertEqual(request_post.status, RecommendationStatusEnum.ACCEPTED)
        self.assertEqual(request_post.requester, requester_company._id)
        self.assertEqual(request_post.recipient, self.company._id)
        self.assertEqual(request_post.viewed, False)
        self.assertEqual(request_post.requester_email, requester_user.email)

        self.assertEqual(RecommendationRequest.objects.count(), 3)

        data = RecommendInitialsView.generate_data_obj(self.company, self.company, self.employee)
        self.assertIsNotNone(data)
        self.assertIn('sent_not_accepted_list', data)
        self.assertIn('sent_accepted_list', data)
        self.assertIn('received_accepted', data)
        self.assertIn('received_not_accepted', data)
        self.assertIn('max_req_count_reached', data)

        sent_not_accepted_list = data['sent_not_accepted_list']
        sent_accepted_list = data['sent_accepted_list']
        received_accepted = data['received_accepted']
        received_not_accepted = data['received_not_accepted']
        max_req_count_reached = data['max_req_count_reached']

        self.assertEqual(max_req_count_reached, False)
        self.assertEqual(len(sent_not_accepted_list), 0)
        self.assertEqual(len(sent_accepted_list), 0)
        self.assertEqual(len(received_accepted), 1)
        self.assertEqual(len(received_not_accepted), 2)

    def testInitialModuleDataRequest(self):
        SettingsManager.set_property('rnes', 3)
        SettingsManager.set_property('rmax', 3)
        self.register(verified=False)

        self.login()
        mail.outbox = []

        companies = self.register_companies(3)

        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : companies[0].rek_id}, {'message' : "!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecommendationRequest.objects.count(), 1)

        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : companies[1].rek_id}, {'message' : "!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecommendationRequest.objects.count(), 2)

        response = self.client.post('/recommendations/ask/%(rek_id)s/' % {'rek_id' : companies[2].rek_id}, {'message' : "!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecommendationRequest.objects.count(), 3)

        RecommendationRequest.objects.update({'_id' : RecommendationRequest.objects.get_one({})._id},
                                             {'$set' : {'status' : RecommendationStatusEnum.ACCEPTED}})


        data = RecommendInitialsView.generate_data_obj(self.company, self.company, self.employee)
        self.assertIsNotNone(data)
        self.assertIn('sent_not_accepted_list', data)
        self.assertIn('sent_accepted_list', data)
        self.assertIn('received_accepted', data)
        self.assertIn('received_not_accepted', data)
        self.assertIn('max_req_count_reached', data)

        sent_not_accepted_list = data['sent_not_accepted_list']
        sent_accepted_list = data['sent_accepted_list']
        received_accepted = data['received_accepted']
        received_not_accepted = data['received_not_accepted']
        max_req_count_reached = data['max_req_count_reached']

        self.assertEqual(max_req_count_reached, True)
        self.assertEqual(len(sent_not_accepted_list), 2)
        self.assertEqual(len(sent_accepted_list), 1)
        self.assertEqual(len(received_accepted), 0)
        self.assertEqual(len(received_not_accepted), 0)

    def testInitialModuleDataNoInvites(self):
        self.register()

        self.login()

        data = RecommendInitialsView.generate_data_obj(self.company, self.company, self.employee)
        self.assertIsNotNone(data)
        self.assertIn('sent_invites', data)
        self.assertIn('sent_registered_invites', data)
        self.assertEqual(len(data['sent_invites']), 0)
        self.assertEqual(len(data['sent_registered_invites']), 0)

    def testInitialModuleDataInvited(self):
        self.register()

        self.login()

        self.client.post('/invites/send/', {'msg' : '1', 'email' : 'someemail@somedomain.zz'})
        self.client.post('/invites/send/', {'msg' : '2', 'email' : 'someemail2@somedomain.zz'})
        self.client.post('/invites/send/', {'msg' : '3', 'email' : 'someemail3@somedomain.zz'})

        data = RecommendInitialsView.generate_data_obj(self.company, self.company, self.employee)
        self.assertIsNotNone(data)
        self.assertIn('sent_invites', data)
        self.assertIn('sent_registered_invites', data)

        self.assertEqual(len(data['sent_invites']), 3)
        self.assertEqual(len(data['sent_registered_invites']), 0)

        invites = {}
        for invite_item in data['sent_invites']:
            invites[invite_item['email']] = 'exists'

        self.assertIn('someemail@somedomain.zz', invites)
        self.assertIn('someemail2@somedomain.zz', invites)
        self.assertIn('someemail3@somedomain.zz', invites)

    def testInitialModuleDataInvitedRegistered(self):
        self.register()

        self.login()

        self.client.post('/invites/send/', {'msg' : '1', 'email' : 'someemail@somedomain.zz'})
        self.client.post('/invites/send/', {'msg' : '2', 'email' : 'someemail2@somedomain.zz'})
        self.client.post('/invites/send/', {'msg' : '3', 'email' : 'someemail3@somedomain.zz'})

        company = Company({'brand_name' : 'new company', 'rek_id' : 'CCCC'})
        company.save()
        rec_request = RecommendationRequest({'requester' : company._id,
                                             'recipient' : self.company._id,
                                             'status' : RecommendationStatusEnum.ACCEPTED,
                                             'message' : '123',
                                             'requester_email' : 'fake@email.zz'})
        rec_request.save()
        invite = Invite.objects.get_one({'email' : 'someemail@somedomain.zz'})
        invite.rec_request = rec_request._id
        invite.save()

        data = RecommendInitialsView.generate_data_obj(self.company, self.company, self.employee)
        self.assertIsNotNone(data)
        self.assertIn('sent_invites', data)
        self.assertIn('sent_registered_invites', data)

        self.assertEqual(len(data['sent_invites']), 2)
        self.assertEqual(len(data['sent_registered_invites']), 1)

        invites = {}
        for invite_item in data['sent_invites']:
            invites[invite_item['email']] = 'exists'

        self.assertIn('someemail2@somedomain.zz', invites)
        self.assertIn('someemail3@somedomain.zz', invites)

