import urllib2
import datetime
from lxml import etree

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from football365.models import Call

class Command(BaseCommand):
    help = "Fetch feeds from Football365 and pass to handlers."

    pipeline = {
        'table': ('table_raw', 'xml2dom', 'table_structure'),
        'fixtures': ('fixtures_raw', 'xml2dom', 'fixtures_structure'),
    }

    @transaction.commit_on_success
    def handle(self, *args, **options):
        for call in Call.objects.all():
            data = None
            for handler in self.pipeline[call.call_type]:
                data = getattr(self, handler)(call, data)
    
    def _raw(self, service, dt, di=None, ci=None):
        """Common method"""
        url = "%s/%s?cl=%s&dt=%s&di=%s" % (
            settings.FOOTBALL365['url'],
            service,
            settings.FOOTBALL365['client_id'],
            dt,
            di or ci
        )
        result = ''
        try:
            f = urllib2.urlopen(url)
            result = f.read()
            f.close()
        except urllib2.URLError:
            pass

        return result

    def xml2dom(self, call, data):
        return etree.fromstring(data)

    def table_raw(self, call, data):
        return self._raw('tablesfeed', 'TablesFS1', di=call.football365_service_id)

    def table_structure(self, call, data):
        result = []
        for row in data.findall('ROW'):
            result.append(dict(
                POSITION=int(row.get('POSITION')),
                TEAM=row[0].text,
                TEAMCODE=row[1].text,
                PLAYED=int(row[2].text),
                WON=int(row[3].text),
                DRAWN=int(row[4].text),
                LOST=int(row[5].text),
                GOALSFOR=int(row[6].text),
                GOALSAGAINST=int(row[7].text),
                GOALDIFFERENCE=int(row[8].text),
                POINTS=int(row[9].text),
            ))
        return result

    def fixtures_raw(self, call, data):
        return self._raw('fixturesfeed', 'Fixtures', di=call.football365_service_id)

    def fixtures_structure(self, call, data):
        result = []
        for day in data.findall('DAY'):
            for row in day[0][0][0].findall('MATCH'):

                # We want a UTC-0 time
                raw_starttime = '%s %s' % (day.get('DATE'), row[3].text)                
                starttime = datetime.datetime.strptime(raw_starttime, '%d/%m/%Y %H:%M')
                tz = int(row[3].get('TIMEZONE').replace('GMT', ''))
                starttime = starttime - datetime.timedelta(hours=tz)

                result.append(dict(
                    HOMETEAM=row[0].text,
                    AWAYTEAM=row[1].text,
                    VENUE=row[2].text,
                    STARTTIME=starttime
                ))
        return result
