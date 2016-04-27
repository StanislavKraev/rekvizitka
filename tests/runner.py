from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner
from rek.mongo.conn_manager import mongodb_connection_manager

class NoDbTestRunner(DjangoTestSuiteRunner):
  """ A test runner to test without database creation """

  def setup_databases(self, **kwargs):
    """ Override the database creation defined in parent class """
    pass

  def teardown_databases(self, old_config, **kwargs):
    """ Override the database teardown defined in parent class """
    pass

class MongoDBTestRunner(DjangoTestSuiteRunner):
    test_db = None

    def setup_databases(self, **kwargs):
      MongoDBTestRunner.test_db = mongodb_connection_manager.database

    def teardown_databases(self, old_config, **kwargs):
        mongodb_connection_manager.connection.drop_database(settings.MONGODB_DB_NAME)
        MongoDBTestRunner.test_db = None
