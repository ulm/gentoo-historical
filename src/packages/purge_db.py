#!/usr/bin/python -OO

import os
import config
import ebuilddb

def delete_ebuild(db,ebuild):
    category, name, version = ebuild[:3]
    c = db.cursor()
    query = ('DELETE FROM ebuild WHERE category="%s" AND name="%s" '
        'AND version="%s"' % (category,name,version))
    #print query
    c.execute(query)

def delete_package(db,package):
    category, name = package[:2]
    c = db.cursor()
    query = ('DELETE FROM package WHERE name="%s" AND category="%s"' %
        (name,category))
    #print query
    c.execute(query)

def get_path(ebuild):
    category, name, version = ebuild[:3]
    ebuild_fname = os.path.join(config.PORTAGE_DIR,category,name,
        '%s-%s.ebuild' % (name,version))
    return ebuild_fname

def ebuilds_in_package(db,package):
    """using db database, return ebuilds in package"""
    category, name = package[:2]
    c = db.cursor()
    query =('SELECT * FROM ebuild WHERE category="%s" AND NAME="%s"'
        % (category,name))
    c.execute(query)
    results = c.fetchall()
    return results

def purge_ebuilds(db):
    """Purge the ebuild table"""
    c = db.cursor()
    query = ('SELECT * FROM ebuild')
    c.execute(query)
    
    while 1:
        ebuild = c.fetchone()
        if not ebuild: break
        path = get_path(ebuild)
        
        if not os.path.exists(path):
            print path,' does not exist.'
            delete_ebuild(db,ebuild)


def purge_packages(db):
    """Purge the package table"""
    c = db.cursor()
    query = ('SELECT * FROM package')
    c.execute(query)
    
    while 1:
        package = c.fetchone()
        if not package: break
        count = len(ebuilds_in_package(db,package))
        if not count:
            delete_package(db,package)

def main():
    db = ebuilddb.db_connect()
    purge_ebuilds(db)
    purge_packages(db)


if __name__ == '__main__':
    main()
