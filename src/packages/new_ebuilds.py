#!/usr/bin/python -OO

__revision__ = "$Revision: 1.1 $"
# $Source: /var/cvsroot/gentoo/src/packages/new_ebuilds.py,v $

import sys
import gentoo
import ebuilddb

def new_to_html(db):
    """Gather new ebuilds and convert to HTML"""
    
    new_ebuilds = gentoo.get_most_recent(db, new = True)
    
    html_list = [gentoo.ebuild_to_html(gentoo.query_to_dict(i), new = True, 
        show_bugs = False) for i in new_ebuilds]
        
    return '\n'.join(html_list)
    
    
def bumps_to_html(db):
    """Gather revision bumps and convert to HTML"""
    
    bumps = gentoo.get_most_recent_bumps(db)
    html_list = [gentoo.ebuild_to_html(gentoo.query_to_dict(i)) for i in bumps]
        
    return '\n'.join(html_list)
    
def new_to_rss(db):
    """Gather new ebuilds and convert to RSS"""
    
    new_ebuilds = gentoo.get_most_recent(db, new = True)
    eb_dict = [gentoo.query_to_dict(i) for i in new_ebuilds]
    gentoo.ebuilds_to_rss(sys.stdout, eb_dict, simple = True, 
        subtitle = 'New Packages')
    
if __name__ == '__main__':
    db = ebuilddb.db_connect()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'rss':
            new_to_rss(db)
        if sys.argv[1] == 'bumps':
            print bumps_to_html(db)
    
    else:
        print new_to_html(db)
