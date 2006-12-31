#!/usr/bin/python -OO

__revision__ = "$Revision: 1.1 $"
# $Source: /var/cvsroot/gentoo/src/packages/genxml.py,v $

from p_objects import *

def to_xml(p_object):
    """Converts portage objects to XML"""

    if isinstance(p_object, Ebuild):
        begin = ('<ebuild category="%s" name="%s" version="%s" found="%s">' %
            (p_object.category, p_object.name, p_object.version, 
            p_object.when_found.gmtime().strftime("%a, %d %b %Y %H:%M:%S +0000")))
        end = '</ebuild>'

        return '\n                '.join([begin] +  ['<arch>%s</arch>' % x 
            for x in p_object.archs] + [end])
    
    elif isinstance(p_object, Package):
        begin = '<package category="%s" name="%s">' % (p_object.category, 
            p_object.name)
        end = '</package>'
        description = ('<description><![CDATA[%s]]></description>' 
            % p_object.description)
        homepage = ''.join(['<homepage><![CDATA[%s]]></homepage>' 
            % x for x in p_object.homepages])
        license = ''.join(['<license>%s</license>' % x for x in
                p_object.licenses])

        return '\n            '.join([begin, description, homepage, license] +
                [to_xml(ebuild) for ebuild in p_object.ebuilds] + [end])

    elif isinstance(p_object, Category):
        begin = '<category name="%s">' % p_object.name
        end = '</category>'

        return '\n        '.join([begin] + [to_xml(package) for package in 
            p_object.packages] + [end])
            
    elif isinstance(p_object, SubArch):
        begin = ('<portage arch="%s" branch="%s">' 
            % (p_object.arch, p_object.sub))
        end = '</portage>'
        string = ''
        string = '\n    '.join([begin] + [to_xml(category) for category in
            p_object.categories] + [end])
        return string
        
    else:
        return '\n\t<!-- Do not know how to xmlize %s -->' % p_object

if __name__ == '__main__':
    from ebuilddb import db_connect
    import os
    
    db = db_connect()
    collection = ArchCollection()
    factory = CategoryFactory(db)
    for arch in config.ARCHLIST:
        for sub in SUBARCHS:
            print arch, sub
            categories = [factory.create(arch, sub, category.name) 
                for category in factory.get(arch, sub)]
            collection.collection[arch][sub].set_categories(categories)
            filename = collection.collection[arch][sub].xml_filename
            #print filename
            new_filename = filename + '.new'
            f_object = open(new_filename,'w')
            f_object.write('<?xml version="1.0" encoding="iso-8859-1"?>\n')
            f_object.write(to_xml(collection.collection[arch][sub]))
            f_object.close()
            os.rename(new_filename, filename)
