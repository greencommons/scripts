import re, uuid, os.path
from lxml import etree
from dateutil.parser import parse
import requests, pytz

from pdb import set_trace

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

# open onix
# for each file in onix, print out title and id

onix_file = './gccorpus/ip/BV_ONIX_feed_island_nodatelimit_ISBNGroup_364.xml'


RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                 u'|' + \
                 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                 (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                  unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                  unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))

with open(onix_file, 'r') as fp:
    root = etree.fromstring(fp.read())

    products = root.xpath('/ONIXMessage/Product')

    products = products[477:]
    
    for product in products:

        # title and subtitle
        titles = []
        titles.append(product.xpath('Title/TitleText')[0].text)
        print product.xpath('Title/TitleText')[0].text.encode('utf-8')

        if len(product.xpath('Title/Subtitle')):
            titles.append(product.xpath('Title/Subtitle')[0].text)
            print product.xpath('Title/Subtitle')[0].text.encode('utf-8')
    
        # id
        id = product.xpath('ProductIdentifier/IDValue')[0].text

        # creators and contributors
        creators = []
        contributors = []
        for contributor in product.xpath('Contributor/PersonName'):

            if contributor.text[0] in ['A', 'a']:
                creators.append(contributor.text)
                print contributor.text.encode('utf-8')
            else:
                contributors.append(contributor.text)
                print contributor.text.encode('utf-8')


        # publisher
        publisher = product.xpath('Publisher/PublisherName')[0].text
        print publisher.encode('utf-8')

        # pub date
        pub_dates = []
        pub_date = product.xpath('PublicationDate')[0].text
        
        pd = parse(pub_date)
        #set_trace()
        local = pytz.timezone("US/Eastern")
        local_dt = local.localize(pd, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        pub_dates.append(utc_dt.strftime ("%Y-%m-%dT%H:%M:%SZ"))

        langs = []
        # lang
        for lang in product.xpath('Language/LanguageCode'):
            langs.append(lang.text)
            print lang.text

        # content
        content_file = 'gccorpus/ip-extracted/%s.txt' % id
        content = ''
        if os.path.exists(content_file):
            with open(content_file, 'r') as epub:
                content = epub.read()
                # AWS CloudSearch seems to have a size limit of 1048576 bytes
                content = content[:1000000]

            print ""

            docs = []

            content = re.sub(RE_XML_ILLEGAL, "?", content)
            content = unicode(content, 'utf-8')

        doc = {'type': 'add', 'id': str(uuid.uuid1()),
            'fields': {
                    'title': titles,
                    'identifier': [id],
                    'creator': creators,
                    'contributor': contributors,
                    'publisher': [publisher],
                    'date': pub_dates,
                    'language': langs,
                    'content': [content],
                    }
            }

        docs.append(doc)

        url = 'our cloudsearch batch endpoint'
        r = requests.post(url, json=docs)
        print titles[0]
        print r.status_code
        print r.text
        print ""