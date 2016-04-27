# -*- coding: utf-8 -*-
from rek.tests.base import BaseTestCase
from rek.utils.model_fields import is_valid_inn

class UtilsTestCase(BaseTestCase):
    def testInnValidator(self):
        invalid_inn = "1234567890"
        invalid_inn_phys = "123456789012"
        valid_inn_phys = "440111639705"
        valid_inn = "7816115023"

        self.assertTrue(is_valid_inn(valid_inn))
        self.assertTrue(is_valid_inn(valid_inn_phys))

        self.assertFalse(is_valid_inn(invalid_inn))
        self.assertFalse(is_valid_inn(invalid_inn_phys))