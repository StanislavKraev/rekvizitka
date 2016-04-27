# -*- coding: utf-8 -*-

from django.utils import simplejson
from rek.contractors.models import Contractor, ContractorStatusEnum, ContractorPrivacy
from rek.contractors.views import make_company_contractor
from rek.rekvizitka.models import Company

from rek.tests.base import BaseTestCase

class ContractorsTestCase(BaseTestCase):
    collection_names = ['users', 'companies', 'company_employees', 'sessions', 'user_activation_links',
                        'billing_accounts', 'deferred_notifications', 'contractors']

    def make_contractor(self, source_company, target_company,
                        status=ContractorStatusEnum.RECEIVED,
                        company1_kwargs=None,
                        company2_kwargs=None,
                        skip_company_contractors_push = False):
        company1_kwargs = company1_kwargs or {}
        company2_kwargs = company2_kwargs or {}

        company1_data = {'rek_id': source_company.rek_id,
                         'brand_name': source_company.brand_name,
                         'logo': source_company.get_logo_url(),
                         'kind_of_activity': source_company.category_text,
                         'employee_id': source_company.owner_employee_id,
                         'privacy': ContractorPrivacy.VISIBLE_EVERYONE}
        company1_data.update(company1_kwargs)

        company2_data = {'rek_id': target_company.rek_id,
                         'brand_name': target_company.brand_name,
                         'logo': target_company.get_logo_url(),
                         'kind_of_activity': target_company.category_text,
                         'employee_id': target_company.owner_employee_id,
                         'privacy': ContractorPrivacy.VISIBLE_EVERYONE}
        company2_data.update(company2_kwargs)

        new_contractor = Contractor({'company_1': source_company._id,
                                     'company_2': target_company._id,
                                     'company_1_data': company1_data,
                                     'company_2_data': company2_data,
                                     'status' : status})

        new_contractor.save()

        if not skip_company_contractors_push:
            Company.objects.collection.update({'_id' : source_company._id},
                    {'$push' : {'contractors' : make_company_contractor(target_company)}})
            Company.objects.collection.update({'_id' : target_company._id},
                    {'$push' : {'contractors' : make_company_contractor(source_company)}})
        return new_contractor

    def test_send_partnership_request(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]

        response = self.client.post('/contractors/add/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contractor.objects.count(), 1)
        self.assertNotIn('error', response.content)
        target_company_upd = Company.objects.collection.find_one({'_id' : target_company._id})
        self.assertIn('contractors', target_company_upd)
        self.assertIsInstance(target_company_upd['contractors'], list)
        self.assertEqual(len(target_company_upd['contractors']), 0)

        new_contractor = Contractor.objects.collection.find_one({})
        self.assertIn('company_1_data', new_contractor)
        self.assertIn('company_2_data', new_contractor)

        company_1_data = new_contractor['company_1_data']
        company_2_data = new_contractor['company_2_data']

        self.assertIn('rek_id', company_1_data)
        self.assertIn('rek_id', company_2_data)

        self.assertIn('logo', company_1_data)
        self.assertIn('logo', company_2_data)

        self.assertIn('brand_name', company_1_data)
        self.assertIn('brand_name', company_2_data)

        self.assertIn('kind_of_activity', company_1_data)
        self.assertIn('kind_of_activity', company_2_data)

        self.assertIn('employee_id', company_1_data)
        self.assertIn('employee_id', company_2_data)

        self.assertIn('privacy', company_1_data)
        self.assertIn('privacy', company_2_data)

    def test_send_partnership_request_wo_rek_id(self):
        self.register()
        self.login()

        response = self.client.post('/contractors/add/', {})
        self.assertEqual(response.status_code, 404)

    def test_send_partnership_request_missed_rek_id(self):
        self.register()
        self.login()

        response = self.client.post('/contractors/add/', {'rek_id' : '1234'})
        self.assertEqual(response.status_code, 404)

    def test_send_partnership_request_exists(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]

        response = self.client.post('/contractors/add/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.content)
        response = self.client.post('/contractors/add/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.content)

    def test_partners_initials_my(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company)

        response = self.client.get('/%s/contractors/i/' % self.company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('own', data)
        self.assertTrue(data['own'])
        self.assertIn('rek_id', data)
        self.assertIn('category_text', data)
        self.assertIn('brand_name', data)
        self.assertIn('rek_partners', data)
        self.assertIn('incoming_requests', data)
        self.assertIn('outgoing_requests', data)
        self.assertIn('company_logo', data)

        outgoing = data['outgoing_requests']
        self.assertEqual(len(outgoing), 1)
        o_req = outgoing[0]
        self.assertIn('logo', o_req)
        self.assertIn('kind_of_activity', o_req)
        self.assertIn('rek_id', o_req)
        self.assertIn('brand_name', o_req)
        self.assertIn('employee_id', o_req)
        self.assertIn('privacy', o_req)
        self.assertIn('viewed', o_req)

        self.assertEqual(o_req['logo'], '')
        self.assertEqual(o_req['kind_of_activity'], 'Testing')
        self.assertEqual(o_req['brand_name'], 'Test Company Brand 0')
        self.assertEqual(o_req['rek_id'], '15000')

        incoming = data['incoming_requests']
        self.assertEqual(len(incoming), 0)

        self.assertEqual(data['rek_id'], self.company.rek_id)
        self.assertEqual(data['category_text'], self.company.category_text)
        self.assertEqual(data['brand_name'], self.company.brand_name)
        self.assertEqual(data['company_logo'], self.company.get_logo_url())
        self.assertEqual(len(data['rek_partners']), 0)

    def test_partners_initials_not_my(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company)

        response = self.client.get('/%s/contractors/i/' % target_company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('own', data)
        self.assertFalse(data['own'])
        self.assertIn('rek_id', data)
        self.assertIn('category_text', data)
        self.assertIn('brand_name', data)
        self.assertIn('rek_partners', data)
        self.assertIn('incoming_requests', data)
        self.assertIn('outgoing_requests', data)
        self.assertIn('company_logo', data)

    def test_partners_initials_unauthorized(self):
        self.register()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company)

        response = self.client.get('/%s/contractors/i/' % target_company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('own', data)
        self.assertFalse(data['own'])
        self.assertIn('rek_id', data)
        self.assertIn('category_text', data)
        self.assertIn('brand_name', data)
        self.assertIn('rek_partners', data)
        self.assertIn('incoming_requests', data)
        self.assertIn('outgoing_requests', data)
        self.assertIn('company_logo', data)

    def test_delete_contractor(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company, status=ContractorStatusEnum.ACCEPTED)

        my_company_upd = Company.objects.get_one({'_id' : self.company._id})
        target_company_upd = Company.objects.get_one({'_id' : target_company._id})

        self.assertEqual(len(my_company_upd.contractors), 1)
        self.assertEqual(len(target_company_upd.contractors), 1)

        response = self.client.post('/contractors/delete/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)
        self.assertEqual(Contractor.objects.count(), 0)

        my_company_upd = Company.objects.get_one({'_id' : self.company._id})
        target_company_upd = Company.objects.get_one({'_id' : target_company._id})

        self.assertEqual(len(my_company_upd.contractors), 0)
        self.assertEqual(len(target_company_upd.contractors), 0)

    def test_partners_initials_not_my_accepted(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company, status=ContractorStatusEnum.ACCEPTED)

        response = self.client.get('/%s/contractors/i/' % target_company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('incoming_requests', data)
        self.assertIn('outgoing_requests', data)
        self.assertIn('rek_partners', data)

        self.assertEqual(len(data['incoming_requests']), 0)
        self.assertEqual(len(data['outgoing_requests']), 0)
        self.assertEqual(len(data['rek_partners']), 1)
        partner = data['rek_partners'][0]

        self.assertIn('logo', partner)
        self.assertIn('kind_of_activity', partner)
        self.assertIn('rek_id', partner)
        self.assertIn('brand_name', partner)
        self.assertIn('employee_id', partner)
        self.assertIn('privacy', partner)
        self.assertIn('viewed', partner)

        self.assertEqual(partner['rek_id'], self.company.rek_id)

    def test_partners_initials_unauthorized_accepted(self):
        self.register()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company, status=ContractorStatusEnum.ACCEPTED)

        response = self.client.get('/%s/contractors/i/' % target_company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('incoming_requests', data)
        self.assertIn('outgoing_requests', data)
        self.assertIn('rek_partners', data)

        self.assertEqual(len(data['incoming_requests']), 0)
        self.assertEqual(len(data['outgoing_requests']), 0)
        self.assertEqual(len(data['rek_partners']), 1)
        partner = data['rek_partners'][0]

        self.assertIn('logo', partner)
        self.assertIn('kind_of_activity', partner)
        self.assertIn('rek_id', partner)
        self.assertIn('brand_name', partner)
        self.assertIn('employee_id', partner)

    def test_delete_contractor_unauth(self):
        self.register()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company, status=ContractorStatusEnum.ACCEPTED)

        response = self.client.post('/contractors/delete/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 302)

    def test_incoming_request(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        self.make_contractor(target_company, self.company)

        response = self.client.get('/%s/contractors/i/' % self.company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('own', data)
        self.assertTrue(data['own'])
        self.assertIn('rek_id', data)
        self.assertIn('category_text', data)
        self.assertIn('brand_name', data)
        self.assertIn('rek_partners', data)
        self.assertIn('incoming_requests', data)
        self.assertIn('outgoing_requests', data)
        self.assertIn('company_logo', data)

        outgoing = data['outgoing_requests']
        self.assertEqual(len(outgoing), 0)

        incoming = data['incoming_requests']
        self.assertEqual(len(incoming), 1)

        i_req = incoming[0]
        self.assertIn('logo', i_req)
        self.assertIn('kind_of_activity', i_req)
        self.assertIn('rek_id', i_req)
        self.assertIn('brand_name', i_req)
        self.assertIn('employee_id', i_req)

        self.assertEqual(i_req['logo'], '')
        self.assertEqual(i_req['kind_of_activity'], 'Testing')
        self.assertEqual(i_req['brand_name'], 'Test Company Brand 0')
        self.assertEqual(i_req['rek_id'], '15000')

    def test_accept_request(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        new_contractor = self.make_contractor(target_company, self.company, skip_company_contractors_push = True)

        response = self.client.post('/contractors/accept/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)

        new_contractor_upd = Contractor.objects.get_one({'_id' : new_contractor._id})
        self.assertIsNotNone(new_contractor_upd)
        self.assertEqual(new_contractor_upd.status, ContractorStatusEnum.ACCEPTED)

        company1_upd = Company.objects.get_one({'_id' : self.company._id})
        company2_upd = Company.objects.get_one({'_id' : target_company._id})

        self.assertEqual(len(company1_upd.contractors), 1)
        self.assertIn('company_id', company1_upd.contractors[0])
        self.assertEqual(company1_upd.contractors[0]['company_id'], target_company._id)

        self.assertEqual(len(company2_upd.contractors), 1)
        self.assertIn('company_id', company2_upd.contractors[0])
        self.assertEqual(company2_upd.contractors[0]['company_id'], self.company._id)


    def test_save_settings(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        new_contractor = self.make_contractor(self.company, target_company, ContractorStatusEnum.ACCEPTED)

        response = self.client.post('/contractors/settings/', {'rek_id' : target_company.rek_id,
                                                               'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)

        new_contractor_upd = Contractor.objects.get_one({'_id' : new_contractor._id})
        self.assertIsNotNone(new_contractor_upd)
        self.assertEqual(new_contractor_upd.company_2_data['privacy'], ContractorPrivacy.VISIBLE_OUR_ADMINS)

    def test_save_settings_reverse(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        new_contractor = self.make_contractor(target_company, self.company, ContractorStatusEnum.ACCEPTED)

        response = self.client.post('/contractors/settings/', {'rek_id' : target_company.rek_id,
                                                               'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)

        new_contractor_upd = Contractor.objects.get_one({'_id' : new_contractor._id})
        self.assertIsNotNone(new_contractor_upd)
        self.assertEqual(new_contractor_upd.company_1_data['privacy'], ContractorPrivacy.VISIBLE_OUR_ADMINS)

    def test_save_settings_not_my(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        new_contractor = self.make_contractor(target_companies[0], target_companies[1], status=ContractorStatusEnum.ACCEPTED)

        response = self.client.post('/contractors/settings/', {'id' : new_contractor._id,
                                                               'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS})
        self.assertEqual(response.status_code, 404)

    def test_accept_request_not_found(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        self.make_contractor(target_company, self.company)

        response = self.client.post('/contractors/accept/', {'rek_id' : 'AABC'})
        self.assertEqual(response.status_code, 404)

    def test_accept_request_unauth(self):
        self.register()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company)

        response = self.client.post('/contractors/accept/', {'rek_id' : 'AABC'})
        self.assertEqual(response.status_code, 302)

    def test_reject_request(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        new_contractor = self.make_contractor(target_company, self.company)

        response = self.client.post('/contractors/reject/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)

        new_contractor_upd = Contractor.objects.get_one({'_id' : new_contractor._id})
        self.assertIsNotNone(new_contractor_upd)
        self.assertEqual(new_contractor_upd.status, ContractorStatusEnum.DECLINED)

    def test_cancel_my_request(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        self.make_contractor(self.company, target_company)

        response = self.client.post('/contractors/delete/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)
        self.assertEqual(Contractor.objects.count(), 0)

    def test_mark_as_viewed(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        contractor = self.make_contractor(target_company, self.company)
        self.assertEqual(contractor.viewed, False)

        response = self.client.post('/contractors/mark_viewed/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.assertNotIn('error', data)

        contractor_upd = Contractor.objects.get_one({'_id' : contractor._id})
        self.assertEqual(contractor_upd.viewed, True)

    #   Visibility tests naming convention
    #
    # test_vis_<auth status>_p<privacy settings>_c<supplementary conditions>
    # where:
    #  auth status:
    #   * unauth         - unauthorized;
    #   * auth_my        - authorized, not my company;
    #   * auth_not_my    - authorized, my company (checking contractor of my company);
    #  privacy settings:
    #   * all            - ContractorPrivacy.VISIBLE_EVERYONE;
    #   * adm            - ContractorPrivacy.VISIBLE_OUR_ADMINS;
    #   * emp            - ContractorPrivacy.VISIBLE_OUR_EMPLOYEES;
    #   * ec             - ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS;
    #   * ecc            - ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS;
    #  supplementary conditions:
    #   * contr          - my & being checked companies are contractors;
    #   * c2             - my & being checked companies are second-tier contractors;
    #   * nc             - my & being checked companies are not contractors at all (1st and 2nd tiers).

    def test_vis_unauth_pall(self):
        target_companies = self.register_companies(2)
        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_EVERYONE},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_EVERYONE})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

    def test_vis_unauth_padm(self):
        target_companies = self.register_companies(2)
        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_unauth_pemp(self):
        target_companies = self.register_companies(2)
        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_unauth_pec(self):
        target_companies = self.register_companies(2)
        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_unauth_pecc(self):
        target_companies = self.register_companies(2)
        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_auth_not_my_pall(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(target_companies[0], target_companies[1],
                             status=ContractorStatusEnum.ACCEPTED,
                             company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_EVERYONE},
                             company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_EVERYONE})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

        response = self.client.get('/%s/contractors/i/' % target_companies[1].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

    def test_vis_auth_not_my_padm(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

        response = self.client.get('/%s/contractors/i/' % target_companies[1].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_auth_my_padm(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_ADMINS})

        response = self.client.get('/%s/contractors/i/' % self.company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

    def test_vis_auth_my_pall(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_EVERYONE},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_EVERYONE})

        response = self.client.get('/%s/contractors/i/' % self.company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

    def test_vis_auth_my_pemp(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES})

        response = self.client.get('/%s/contractors/i/' % self.company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

    def test_vis_auth_my_pec(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS})

        response = self.client.get('/%s/contractors/i/' % self.company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

    def test_vis_auth_my_pecc(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS})

        response = self.client.get('/%s/contractors/i/' % self.company.rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 1)

    def test_vis_auth_not_my_pec_ccontr(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS})

        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 2)

        response = self.client.get('/%s/contractors/i/' % target_companies[1].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_auth_not_my_pec_cnc(self):
        self.register()
        self.login()
        target_companies = self.register_companies(2)

        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

        response = self.client.get('/%s/contractors/i/' % target_companies[1].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_auth_not_my_pec_cc2(self):
        self.register()
        self.login()
        target_companies = self.register_companies(3)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS})

        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS})

        self.make_contractor(target_companies[1], target_companies[2],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES_CONTRACTORS_THEIR_CONTRACTORS})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 2)

        response = self.client.get('/%s/contractors/i/' % target_companies[1].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 2)

        response = self.client.get('/%s/contractors/i/' % target_companies[2].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_vis_auth_not_my_pemp_cc2(self):
        self.register()
        self.login()
        target_companies = self.register_companies(3)
        self.make_contractor(self.company, target_companies[0],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES})

        self.make_contractor(target_companies[0], target_companies[1],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES})

        self.make_contractor(target_companies[1], target_companies[2],
            status=ContractorStatusEnum.ACCEPTED,
            company1_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES},
            company2_kwargs={'privacy' : ContractorPrivacy.VISIBLE_OUR_EMPLOYEES})

        response = self.client.get('/%s/contractors/i/' % target_companies[0].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

        response = self.client.get('/%s/contractors/i/' % target_companies[1].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

        response = self.client.get('/%s/contractors/i/' % target_companies[2].rek_id)
        self.assertEqual(response.status_code, 200)
        data = simplejson.loads(response.content)

        self.assertIn('rek_partners', data)
        self.assertEqual(len(data['rek_partners']), 0)

    def test_cross_request(self):
        self.register()
        self.login()
        target_company = self.register_companies(2)[0]
        contractor = self.make_contractor(target_company, self.company, skip_company_contractors_push=True)

        response = self.client.post('/contractors/add/', {'rek_id' : target_company.rek_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contractor.objects.count(), 1)
        contractor_upd = Contractor.objects.get_one({'_id' : contractor._id})
        self.assertIsNotNone(contractor_upd)
        self.assertEqual(contractor_upd.status, ContractorStatusEnum.ACCEPTED)

        company1_upd = Company.objects.get_one({'_id' : self.company._id})
        company2_upd = Company.objects.get_one({'_id' : target_company._id})

        self.assertEqual(len(company1_upd.contractors), 1)
        self.assertIn('company_id', company1_upd.contractors[0])
        self.assertEqual(company1_upd.contractors[0]['company_id'], target_company._id)

        self.assertEqual(len(company2_upd.contractors), 1)
        self.assertIn('company_id', company2_upd.contractors[0])
        self.assertEqual(company2_upd.contractors[0]['company_id'], self.company._id)

    def test_de_normalization(self):
        pass
