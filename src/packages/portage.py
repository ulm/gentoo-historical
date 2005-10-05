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
"""Portage Objects"""

__revision__ = "$Revision: 1.1.2.3 $"
# $Source: /var/cvsroot/gentoo/src/packages/Attic/portage.py,v $

import sys
import os

# We need to "fake" as repoman so portage will ignore local system settings
os.environ['PORTAGE_CALLER'] = 'repoman'

__name__ = 'tmp'
sys.path = ["/usr/lib/portage/pym"]+sys.path
import portage as portage_api
__name__ = 'portage'
sys.path = sys.path[1:]

PORTAGE_PATH = '/usr/portage'

class Category:
    """Collection of packages"""

    def __init__(self, name, description = ''):
        self.name = name
        self.description = description
        self.packages = []

    def set_packages(self, packages):
        """Set packages for this Category"""
        self.packages = packages

    def get_packages(self):
        """Return package list (implies set_packages() has been called"""
        return self.packages

    def __str__(self):
        return self.name

class CategoryFactory:
    """get returns a list of categories with specified criteria
    create creates a "deep" (populated) category (singular) from specified
    criteria
    """
    def __init__(self, database):
        # shuts up pylint
        self.database = database
        self.cache = {}
        self.pfactory = PackageFactory(self.database)

    def create(self, category):
        """Create a populated category using database database"""
        key = '/%s' % category
        if self.cache.has_key(key):
            return self.cache[key]

        category = Category(category)
        packages = [self.pfactory.create(category.name, package.name)
            for package in self.pfactory.get(category.name)]
        category.set_packages(packages)
        self.cache[key] = category
        return category

    def get(self):
        """Return list of categories from database with specified criteria"""
        key = '/'
        if self.cache.has_key(key):
            return self.cache[key]
        cursor = self.database.cursor()
        query = ('SELECT * FROM category ORDER BY name')
        #print query
        cursor.execute(query)
        results = cursor.fetchall()
        categories = [Category(result[0], result[1]) for result in results]
        self.cache[key] = categories
        return categories

class Package:
    """Collection of ebuilds"""

    def __init__(self, category, name):
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
    def get_ebuilds(self):
        """Return list of ebuilds contained in package"""
        return self.ebuilds

    def to_dict(self):
        """Return Package attributes as a dict"""
        return {
            'category': self.category,
            'name': self.name,
            'homepages': self.homepages,
            'licences': self.licenses,
            'description': self.description,
            'ebuilds': self.ebuilds
        }

    def __str__(self):
        return self.name

class PackageFactory:
    """get or create packages and populate the ebuilds automagically"""

    def __init__(self, database):
        self.database = database
        self.cache = {}
        self.efactory = EbuildFactory(self.database)

    def create(self, category, name):
        """Create fully populated Package"""

        key = '/'.join((category, name))
        if self.cache.has_key(key):
            return self.cache[key]

        package = Package(category, name)
        ebuilds = [Ebuild(category = ebuild.category,
            name = ebuild.name,
            version = ebuild.version,
            when_found = ebuild.when_found,
            description = ebuild.description,
            arch = ','.join(ebuild.archs),
            homepage = ' '.join(ebuild.homepages),
            license = ' '.join(ebuild.licenses),
            changelog = ebuild.changelog,
            masked = ebuild.masked)
            for ebuild in self.efactory.get(category, name)]
        package.set_ebuilds(ebuilds)
        self.cache[key] = package
        return package

    def get(self, category):
        """Return list of (empty) Packages with specified criteria"""
        key = '/%s' % category
        if self.cache.has_key(key):
            return self.cache[key]

        cursor = self.database.cursor()
        query = ('SELECT DISTINCT name FROM ebuild WHERE category = "%s"'
            % category )
        #print query
        cursor.execute(query)
        results = [result[0] for result in cursor.fetchall()]
        packages = [Package(category, name) for name in results]
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
        package_datetime (optional)
    """

    def __init__(self, **kwargs):
        self.category = kwargs['category']
        self.name = kwargs['name']
        self.version = kwargs['version']
        self.when_found = kwargs['when_found']
        self.description = kwargs['description']
        self.archs = kwargs['arch'].split(',')
        self.homepages = kwargs['homepage'].split()
        self.masked = bool(kwargs['masked'])
        if not kwargs.get('license'):
            licenses = ''
        else:
            licenses = kwargs['license'].replace('|',' ')
        # replace |  with space so to split
        self.licenses = licenses.split()
        self.changelog = kwargs['changelog']
        self.package_datetime = kwargs.get('package_datetime')

    def arch_dict(self):
        """Return arch strings as a dictionary of lists"""
        archs = {'stable': [], 'testing': [], 'blocked': []}
        for arch in self.archs:
            if arch[0] == '~':
                archs['testing'].append(arch[1:])
            elif arch[0] == '-':
                archs['blocked'].append(arch[1:])
            else:
                archs['stable'].append(arch)
        return archs

    def arch_string(self):
        """Return archstring as a dictionary of strings"""
        my_dict = self.arch_dict()
        return {'stable': ' '.join(my_dict['stable']),
            'testing': ' '.join(my_dict['testing']) }

    def to_dict(self):
        """Nice little utility method to wrap ebuild attributes into a dict"""
        attributes = {}
        for key in ('category', 'name', 'version', 'when_found', 'description',
            'homepages', 'licenses', 'changelog', 'package_datetime'):
            attributes[key] = getattr(self, key)
        archs = self.arch_dict()
        attributes['stable'] = archs['stable']
        attributes['testing'] = archs['testing']

        return attributes

    def cmp(cls, first, second):
        """Compare two ebuilds"""
        fields_first = portage_api.pkgsplit('%s-%s'
                % (first.name, first.version))
        fields_second = portage_api.pkgsplit('%s-%s'
                % (second.name, second.version))
        return portage_api.pkgcmp(fields_first, fields_second)
    cmp = classmethod(cmp)


class EbuildFactory:
    """Ebuild factory.  We only need the get() method as create would do the
    same thing as Ebuild().  Ebuilds don't need to be populated further down
    """
    def __init__(self, database):
        self.database = database
        self.cache = {}

    def create(self, **kwargs):
        """Just returns Ebuild()"""
        return Ebuild(**kwargs)

    def get(self, category, name, version = None):
        """Given database, return list of Ebuilds"""
        cursor = self.database.cursor()
        if version:
            extra = ' AND ebuild.version = "%s" ' % version
        else:
            extra = ''
        query = ('SELECT ebuild.category, ebuild.name, version, ebuild.when_found, '
            'description, changelog, arch, homepage, ebuild.license, '
            'package.when_found, is_masked FROM ebuild, package '
            'WHERE ebuild.name = "%s" '
            '   AND ebuild.category = "%s" %s '
            '   AND ebuild.name = package.name '
            '   AND ebuild.category = package.category '
            'ORDER by ebuild.when_found DESC'
            % (name, category, extra))
        #print query
        cursor.execute(query)
        results = cursor.fetchall()
        return [Ebuild(category=result[0], name=result[1], version=result[2],
            when_found=result[3], description=result[4], changelog=result[5],
            arch=result[6], homepage=result[7], license=result[8],
            package_datetime=result[9], masked=result[10]) for result
            in results]
