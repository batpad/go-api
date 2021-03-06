import requests
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen
import json
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from api.models import Appeal, AppealDocument
from api.logger import logger


class Command(BaseCommand):
    help = 'Ingest existing appeal documents'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--fullscan',
            action='store_true',
            help='Run a full scan on all appeals',
        )

    def makelist(self, table):
        result = []
        allrows = table.findAll('tr')
        for row in allrows:
            url=''
            for a in row.find_all('a', href=True):
                url = a['href']
            result.append([url])
            allcols = row.findAll('td')
            for col in allcols:
                thestrings = [s.strip() for s in col.findAll(text=True)]
                thetext = ''.join(thestrings)
                result[-1].append(thetext)
        return result

    def parse_date(self, date_string):
        # 21Dec2017
        timeformat = '%d%b%Y'
        return datetime.strptime(date_string.strip(), timeformat).replace(tzinfo=timezone.utc)

    def handle(self, *args, **options):
        logger.info('Starting appeal document ingest')

        if options['fullscan']:
            # If the `--fullscan` option is passed, check ALL appeals
            print('Doing a full scan of all Appeals')
            qset = Appeal.objects.all()
        else:
            # By default, only check appeals for the past 3 months where Appeal Documents is 0
            now = datetime.now()
            three_months_ago = now - relativedelta(months=3)
            qset = Appeal.objects.filter(appealdocument__isnull=True).filter(end_date__gt=three_months_ago)

        # First get all Appeal Codes
        appeal_codes = [a.code for a in qset]

        # Modify code taken from https://pastebin.com/ieMe9yPc to scrape `publications-and-reports` and find
        # Documents for each appeal code
        output = []
        page_not_found = []
        for code in appeal_codes:
            code = code.replace(' ', '')
            docs_url = 'http://www.ifrc.org/en/publications-and-reports/appeals/?ac='+code+'&at=0&c=&co=&dt=1&f=&re=&t=&ti=&zo='
            try:
                response = urlopen(docs_url)
            except: # if we get an error fetching page for an appeal, we ignore it
                page_not_found.append(code)
                continue

            soup = BeautifulSoup(response.read(), "lxml")
            div = soup.find('div', id='cw_content')
            for t in div.findAll('tbody'):
                output = output + self.makelist(t)

        # Once we have all Documents in output, we add all missing Documents to the associated Appeal
        not_found = []
        existing = []
        created = []

        acodes = list(set([a[2] for a in output]))
        for code in acodes:
            try:
                appeal = Appeal.objects.get(code=code)
            except ObjectDoesNotExist:
                not_found.append(code)
                continue

            existing_docs = list(appeal.appealdocument_set.all())
            docs = [a for a in output if a[2] == code]
            for doc in docs:
                exists = len([a for a in existing_docs if a.document_url == doc[0]]) > 0
                if exists:
                    existing.append(doc[0])
                else:
                    try:
                        created_at = self.parse_date(doc[5])
                    except:
                        created_at = None

                    AppealDocument.objects.create(
                        document_url=doc[0],
                        name=doc[4],
                        created_at=created_at,
                        appeal=appeal,
                    )
                    created.append(doc[0])
        logger.info('%s appeal documents created' % len(created))
        logger.info('%s existing appeal documents' % len(existing))
        logger.info('%s pages not found for appeal' % len(page_not_found))
        logger.warn('%s documents without appeals in system' % len(not_found))
