#!/usr/bin/python
#
# Copyright (C) 2005, marduk <marduk@python.net>
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
import config
from elementtree.ElementTree import parse


PORTAGE_DIR = '/usr/portage'

def process(filename):
    """parse filename and return a tree"""

    tree = parse(filename)
    return tree

def update_db(db, category, description):
    c = db.cursor()
    query = ('INSERT INTO category VALUES ("%s", "%s") '
            'ON DUPLICATE KEY UPDATE description="%s"' % (category, description,
                description))
    c.execute(query)

def del_db(db):
    c = db.cursor()
    query = 'DELETE FROM category'
    c.execute(query)
    db.commit()

def main(args):
    directories = os.listdir(PORTAGE_DIR)

    del_db(config.db)
    for directory in directories:
        if '-' not in directory:
            # skip it
            continue
        metadata_file = os.path.join(PORTAGE_DIR, directory, 'metadata.xml')

        description_text = ''
        if os.path.exists(metadata_file):

            tree = process(metadata_file)
            descriptions = tree.findall('longdescription')

            # get English description, if avaliable
            for description in descriptions:
                if description.attrib.has_key('lang') and description.attrib['lang'] == 'en':
                    description_text = description.text.strip()

            if not description_text:
                # we give up and just take the first description available
                description_text = descriptions[0].text.strip()
            if description_text == '':
                print 'No description for %s' % directory
        else:
            print 'Category %s missing metadata.xml' % directory

        #print directory,description.text
        update_db(config.db, directory,description_text)
    config.db.commit()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
