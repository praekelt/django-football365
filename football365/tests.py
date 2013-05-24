import warnings

from django.conf import settings
from django.test import TestCase

from football365.models import Call
from football365.management.commands import football365_fetch


class TestFetchCommand(football365_fetch.Command):
    pipeline = {
        'table': ('table_raw', 'xml2dom', 'table_structure', 'store_table'),
        'fixtures': ('fixtures_raw', 'xml2dom', 'fixtures_structure', 'store_fixtures'),
        'results': ('results_raw', 'xml2dom', 'results_structure', 'store_results'),
        'live': ('live_raw', 'xml2dom', 'live_structure', 'store_live'),
    }

    def store(self, call_type, call, data):
        if not data:
            warnings.warn('No data for call type %s' % call_type)
        setattr(self, '%s_data' % call_type, data)

    def store_table(self, call, data):
        self.store('table', call, data)

    def store_fixtures(self, call, data):
        self.store('fixtures', call, data)

    def store_results(self, call, data):
        self.store('results', call, data)

    def store_live(self, call, data):
        self.store('live', call, data)


class Football365TestCase(TestCase):

    def test_fetch_command(self):
        service_ids = settings.FOOTBALL365['test_service_ids']
        for choice in Call._meta.get_field_by_name('call_type')[0].choices:
            Call.objects.create(title=choice[1], call_type=choice[0],
                                football365_service_id=service_ids[choice[0]])
        test_command = TestFetchCommand()
        test_command.execute()
        for choice in Call._meta.get_field_by_name('call_type')[0].choices:
            # check that all fields are populated
            for item in getattr(test_command, '%s_data' % choice[0]):
                for key, val in item.iteritems():
                    try:
                        self.assertNotEqual(val, None)
                        self.assertNotEqual(val, '')
                    except AssertionError:
                        raise AssertionError("Value of '%s' is %s in %s item" % (key, val, choice[0]))
