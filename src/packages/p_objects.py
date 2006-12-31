"""Portage Objects"""

# Once tuned, this will hopefully be the interface used in the future for
# packages.g.o

__revision__ = "$Revision: 1.1 $"
# $Source: /var/cvsroot/gentoo/src/packages/p_objects.py,v $
# $Date: 2004/09/17 02:16:17 $

import config

SUBARCHS = ('stable', 'testing', 'all')

class SubArch:
    """Sub Architecture
    We split portage into /<arch>/['stable','testing','all']/
    """

    def __init__(self, arch, sub):
        if sub == 'all':
            self.xml_filename = '%s/archs/%s/portage.xml' % (config.LOCALHOME, 
                arch)
        else:
            self.xml_filename = ('%s/archs/%s/%s/portage.xml' %
            (config.LOCALHOME, arch, sub))
        self.arch = arch
        self.sub = sub
        self.categories = []
        
    def set_categories(self, categories):
        """Set categries of SubArch to categories"""
        self.categories = categories
    
class ArchCollection:
    """Collection of all SubArchitectures"""

    def __init__(self):
        self.collection = {}
        for arch in config.ARCHLIST:
            #print arch
            self.collection[arch] = {}
            for sub in SUBARCHS:
                #print sub
                self.collection[arch][sub] = SubArch(arch, sub)
                
class Category:
    """Collection of packages"""

    def __init__(self, arch, sub, name):
        self.arch = arch
        self.sub = sub
        self.name = name
        self.packages = []

    def set_packages(self, packages):
        """Set packages for this Category"""
        self.packages = packages
    def __str__(self):
        return self.name

class CategoryFactory:
    """get returns a list of categories with specified criteria
    create creates a "deep" (populated) category (singular) from specified
    criteria
    """
    def __init__(self, db):
        # shuts up pylint
        self.db = db
        self.cache = {}
        self.pfactory = PackageFactory(self.db)
        
    def create(self, arch, sub, category):
        """Create a populated category using database db"""
        key = '/'.join((arch, sub, category))
        if self.cache.has_key(key):
            return self.cache[key]
        
        category = Category(arch, sub, category)
        packages = [self.pfactory.create(arch, sub, category.name, package.name) 
            for package in self.pfactory.get(arch, sub, category.name)]
        category.set_packages(packages)
        self.cache[key] = category
        return category
        
    def get(self, arch, sub):
        """Return list of categories from db with specified criteria"""
        key = '/'.join((arch, sub))
        if self.cache.has_key(key):
            return self.cache[key]
        c = self.db.cursor()
        query = ('SELECT DISTINCT category FROM ebuild WHERE 1=1 %s ' 
            % get_extra(arch, sub))
        #print query
        c.execute(query)
        results = [result[0] for result in c.fetchall()]
        categories = [Category(arch, sub, category) for category in results]
        self.cache[key] = categories
        return categories
        
class Package:
    """Collection of ebuilds"""

    def __init__(self, arch, sub, category, name):
        self.arch = arch
        self.sub = sub
        self.category = category
        self.name = name
        self.ebuilds = []
        self.homepages = ''
        self.licenses = ''
        self.description = ''

    def set_ebuilds(self, ebuilds):
        """Populates Package with specified list of ebuilds"""
        self.ebuilds = ebuilds
        if self.ebuilds:
            self.homepages = self.ebuilds[0].homepages
            self.licenses = self.ebuilds[0].licenses
            self.description = self.ebuilds[0].description
            
    def __str__(self):
        return self.name

class PackageFactory:
    """get or create packages and populate the ebuilds automagically"""
    
    def __init__(self, db):
        self.db = db
        self.cache = {}
        self.efactory = EbuildFactory(self.db)
    
    def create(self, arch, sub, category, name):
        """Create fully populated Package"""
        
        key = '/'.join((arch, sub, category, name))
        if self.cache.has_key(key):
            return self.cache[key]
            
        package = Package(arch, sub, category, name)
        ebuilds = [Ebuild(category = ebuild.category, 
            name = ebuild.name,
            version = ebuild.version, 
            when_found = ebuild.when_found,
            description = ebuild.description, 
            arch = ' '.join(ebuild.archs),
            homepage = ' '.join(ebuild.homepages), 
            license = ' '.join(ebuild.licenses),
            changelog = ebuild.changelog)
            for ebuild in self.efactory.get(arch, sub, category, name)]
        package.set_ebuilds(ebuilds)
        self.cache[key] = package
        return package
        
    def get(self, arch, sub, category):
        """Return list of (empty) Packages with specified criteria"""
        key = '/'.join((arch, sub, category))
        if self.cache.has_key(key):
            return self.cache[key]
        
        c = self.db.cursor()
        query = ('SELECT DISTINCT name FROM ebuild WHERE category = "%s" %s'
            % (category, get_extra(arch, sub)))
        #print query
        c.execute(query)
        results = [result[0] for result in c.fetchall()]
        packages = [Package(arch, sub, category, name) for name in results]
        self.cache[key] = packages
        return packages
    
class Ebuild:
    """Classic ebuild
    
    To create a Ebuild object, we expect:
        category
        name
        version
        when_found
        description
        arch (as KEYWORDS in .ebuilds)
        homepage
        license
        changelog (see changelog.py for help in getting this value from portage)
    """

    def __init__(self, **kwargs):
        self.category = kwargs['category']
        self.name = kwargs['name']
        self.version = kwargs['version']
        self.when_found = kwargs['when_found']
        self.description = kwargs['description']
        self.archs = kwargs['arch'].split()
        self.homepages = kwargs['homepage'].split()
        licenses = kwargs['license'].replace('|',' ') 
        # replace |  with space so to split
        self.licenses = licenses.split()
        self.changelog = kwargs['changelog']

class EbuildFactory:
    """Ebuild factory.  We only need the get() method as create would do the
    same thing as Ebuild().  Ebuilds don't need to be populated further down
    """
    def __init__(self, db):
        self.db = db
        self.cache = {}
        
    def get(self, arch, sub, category, name):
        """Given database, db, return list of Ebuilds"""
        c = self.db.cursor()
        query = ('SELECT ebuild.category, ebuild.name, version, when_found, '
            'description, changelog, arch, homepage, license FROM ebuild, '
            'package WHERE ebuild.name = "%s" AND ebuild.category = "%s" AND '
            'ebuild.name = package.name AND ebuild.category = package.category '
            '%s ORDER by when_found DESC' 
            % (name, category, get_extra(arch, sub)))
        #print query
        c.execute(query)
        results = c.fetchall()
        return [Ebuild(category=result[0], name=result[1], version=result[2],
            when_found=result[3], description=result[4], changelog=result[5],
            arch=result[6], homepage=result[7], license=result[8]) for result
            in results]
        
def get_extra(arch, sub):
    """Return extra criteria of a query string according to arch and sub"""
    
    if sub == 'all':
        sub = ''
    if arch == 'all':
        arch = ''
    extra = ''
    if arch:
        stable_extra = ('ebuild.arch REGEXP "^%s| %s" '
            % (arch,arch))
        testing_extra = ('ebuild.arch REGEXP "^~%s| ~%s" '
            % (arch,arch))
        if sub == 'stable':
            extra = ' AND (%s) ' % stable_extra
        elif sub == 'testing':
            extra = ' AND (%s) ' % testing_extra
        else:
            extra = ' AND ((%s) OR (%s)) ' % (stable_extra, testing_extra)
            
    return extra
