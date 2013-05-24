import urllib2
import datetime
from lxml import etree

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from football365.models import Call


class Command(BaseCommand):
    help = """Fetch feeds from Football365 and pass to handlers. Do not call
this command directly. It is intended to be subclassed."""

    pipeline = {
        'table': ('table_raw', 'xml2dom', 'table_structure'),
        'fixtures': ('fixtures_raw', 'xml2dom', 'fixtures_structure'),
        'results': ('results_raw', 'xml2dom', 'results_structure'),
        'live': ('live_raw', 'xml2dom', 'live_structure'),
    }

    @transaction.commit_on_success
    def handle(self, *args, **options):
        for call in Call.objects.all():
            data = None
            for handler in self.pipeline.get(call.call_type, []):
                data = getattr(self, handler)(call, data)

    def _raw(self, service, dt=None, di=None, ci=None, client_id=None, url=None):
        """Common method"""
        url = "%s/%s?cl=%s" % (
            url or settings.FOOTBALL365['url'],
            service,
            client_id or settings.FOOTBALL365['client_id'],
        )
        if dt:
            url = url + "&dt=" + dt
        if di:
            url = url + "&di=" + str(di)
        if ci:
            url = url + "&ci=" + str(ci)

        result = ''
        try:
            f = urllib2.urlopen(url)
            result = f.read()
            # these characters should only appear in tag contents and need to be escaped
            result = result.replace("&", "&amp;").replace("'", "&apos;")
            f.close()
        except urllib2.URLError:
            pass

        return result

    def xml2dom(self, call, data):
        return etree.fromstring(data)

    def table_raw(self, call, data):
        return self._raw(
            'tablesfeed', 'TablesFS1', di=call.football365_service_id,
            client_id=call.client_id, url=call.url
        )

    def table_structure(self, call, data):
        result = []
        for row in data.findall('ROW'):
            result.append(dict(
                POSITION=int(row.get('POSITION')),
                TEAM=row.find('TEAM').text,
                TEAMCODE=row.find('TEAMCODE').text,
                PLAYED=int(row.find('PLAYED').text),
                WON=int(row.find('WON').text),
                DRAWN=int(row.find('DRAWN').text),
                LOST=int(row.find('LOST').text),
                GOALSFOR=int(row.find('GOALSFOR').text),
                GOALSAGAINST=int(row.find('GOALSAGAINST').text),
                GOALDIFFERENCE=int(row.find('GOALDIFFERENCE').text),
                POINTS=int(row.find('POINTS').text),
            ))
        return result

    def fixtures_raw(self, call, data):
        return self._raw(
            'fixturesfeed', 'Fixtures', di=call.football365_service_id,
            client_id=call.client_id, url=call.url
        )

    def fixtures_structure(self, call, data):
        result = []
        for day in data.findall('DAY'):
            for row in day.findall('.//MATCH'):

                # We want a UTC-0 time
                raw_starttime = '%s %s' % (day.get('DATE'), row.find('STARTTIME').text)
                starttime = datetime.datetime.strptime(raw_starttime, '%d/%m/%Y %H:%M')
                tz = int(row.find('STARTTIME').get('TIMEZONE').replace('GMT', ''))
                starttime = starttime - datetime.timedelta(hours=tz)

                result.append(dict(
                    HOMETEAM=row.find('HOMETEAM').text,
                    HOMETEAMCODE=row.find('HOMETEAMCODE').text,
                    AWAYTEAM=row.find('AWAYTEAM').text,
                    AWAYTEAMCODE=row.find('AWAYTEAMCODE').text,
                    VENUE=row.find('VENUE').text,
                    STARTTIME=starttime
                ))
        return result

    def results_raw(self, call, data):
        return self._raw(
            'resultsfeed', 'Results', di=call.football365_service_id,
             client_id=call.client_id, url=call.url
        )

    def results_structure(self, call, data):
        result = []
        for day in data.findall('DAY'):
            for row in day.findall('.//MATCH'):
                result.append(dict(
                    HOMETEAM=row.find('HOMETEAM').text,
                    HOMETEAMCODE=row.find('HOMETEAMCODE').text,
                    AWAYTEAM=row.find('AWAYTEAM').text,
                    AWAYTEAMCODE=row.find('AWAYTEAMCODE').text,
                    HOMETEAMSCORE=int(row.find('HOMETEAMSCORE').text),
                    AWAYTEAMSCORE=int(row.find('AWAYTEAMSCORE').text),
                    DATE=datetime.datetime.strptime(day.get('DATE'), '%d/%m/%Y')
                ))
        return result

    def live_raw(self, call, data):
        return self._raw(
            'footballlive', ci=call.football365_service_id,
            client_id=call.client_id, url=call.url
        )

    def live_structure(self, call, data):
        result = []
        for match in data.findall('.//MATCH'):

            # We want a UTC-0 time
            raw_starttime = '%s %s' % (match.get('FXDATE'), match.get('FXTIME'))
            starttime = datetime.datetime.strptime(raw_starttime, '%Y-%m-%d %H:%M')
            tz = int(match.get('TIMEZONE').replace('GMT', ''))
            starttime = starttime - datetime.timedelta(hours=tz)

            di = dict(
                LIVE=match.get('live') == 'true',
                DATE=starttime,
                HOMETEAM=match.find('HOMETEAM').text,
                HOMETEAMCODE=match.find('HOMETEAMCODE').text,
                AWAYTEAM=match.find('AWAYTEAM').text,
                AWAYTEAMCODE=match.find('AWAYTEAMCODE').text,
                HOMETEAMSCORE=int(match.find('HOMETEAMSCORE').text or 0),
                AWAYTEAMSCORE=int(match.find('AWAYTEAMSCORE').text or 0),
                MATCHSTATUS=match.find('MATCHSTATUS').text,  # xxx: translation issue here
                HOMETEAMGOALS=[],
                AWAYTEAMGOALS=[],
                HOMETEAMCARDS=[],
                AWAYTEAMCARDS=[]
            )

            for scorer in match.find('HOMETEAMGOALS').findall('SCORER'):
                di['HOMETEAMGOALS'].append(scorer.text)
            for scorer in match.find('AWAYTEAMGOALS').findall('SCORER'):
                di['AWAYTEAMGOALS'].append(scorer.text)
            for card in match.find('HOMETEAMCARDS').findall('CARD'):
                di['HOMETEAMCARDS'].append(card.text)
            for card in match.find('AWAYTEAMCARDS').findall('CARD'):
                di['AWAYTEAMCARDS'].append(card.text)

            result.append(di)

        return result
