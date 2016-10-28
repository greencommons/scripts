import re, uuid, os.path
from datetime import datetime
import requests, pytz, json


from pdb import set_trace

import sys  


from HTMLParser import HTMLParser


# thanks, http://stackoverflow.com/a/925630
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()



reload(sys)  
sys.setdefaultencoding('utf8')

# open onix
# for each file in onix, print out title and id

ted_file = './greenTED.json'


RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                 u'|' + \
                 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                 (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                  unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                  unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))

with open(ted_file, 'r') as fp:
    talks = json.loads(fp.read())   
    
    docs = []
    for talk in talks:    

        # title and subtitle
        titles = []
        titles.append(talk['title'])
        print titles

        # id
        id = talk['talkid']
        #print id

        # creators and contributors
        creators = []
        creators.append(talk['author'])

        # date
        date = datetime.strptime(talk['ddate'].strip(), "%b %Y")
        local = pytz.timezone("US/Eastern")
        local_dt = local.localize(date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        dates = []
        dates.append(utc_dt.strftime ("%Y-%m-%dT%H:%M:%SZ"))

        # description
        description = []
        description.append(talk['description'])

        # content
        content = []
        content.append(strip_tags(talk['transcript']))
        
        # subjects
        subject = talk['tags'].split(', ')


        doc = {'type': 'add', 'id': str(uuid.uuid1()),
            'fields': {
                    'title': titles,
                    'identifier': [id],
                    'creator': creators,
                    'publisher': ['TED'],
                    'date': dates,
                    'language': ['eng'],
                    'description': description,
                    'content': content,
                    'subject': subject,
                    }
            }

        docs.append(doc)

    #print json.dumps(docs[0], sort_keys=True, indent=4, separators=(',', ': '))

    url = 'our cloudsearch batch endpoint'
    r = requests.post(url, json=docs)
    print r.status_code
    print r.text
    print ""





