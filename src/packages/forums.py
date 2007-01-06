
"""Functions that deal with interfacing with forums.gentoo.org"""

import urllib

BASE_URL = 'http://forums.gentoo.org/'
# Right now we just have a search thingie


def get_search_url_from_pkg(pkg):
    """Return HTTP url based on pkg"""
    
    params = {'search_keywords': pkg['name'],
        'search_terms': 'all',
        'show_results':'topics',
        'mode': 'results'
        }
    
    query = urllib.urlencode(params)
    return '%s/search.php?%s' % (BASE_URL, query)
    
    
def create_forums_link(pkg):
    
    return ('<a title="forums.gentoo.org" href="%s" >Forums</a>' 
        % get_search_url_from_pkg(pkg).replace('&','&amp;')
        )
