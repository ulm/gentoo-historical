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
"""
/portage: The portage browser interface

will be called as:
    /portage/                       list categories
    /portage/<category>/            list packages in category
    /portage/<category>/<package>/  list ebuilds in package
    /portage/<category>/<package>/<version>/ shows the ebuild
    /portage/<meta>/                lists categories in special "meta" category
                                    (the part before the "-")

    Most of the UI work for packages and ebuilds is done in packages.ui
"""

_q_exports = []

from os.path import exists
from quixote import redirect
from quixote.html import htmltext, html_quote
from quixote.util import StaticFile
from packages import portage
from packages.ui import ebuild, package
from packages.ui.main import page, sidebox
from packages import config

database = config.db

def _q_index(_):
    """/portage/"""
    cat_factory = portage.CategoryFactory(database)
    categories = cat_factory.get()

    # We need to find out how many packages are in each category
    pkg_factory = portage.PackageFactory(database)
    for category in categories:
        category.set_packages(pkg_factory.get(category.name))

    body = ('<h3 class="title">Portage Categories</h3>'
        '<ul class="categoryList">\n' +
        '\n'.join(['<li><a href="%s/">%s</a> (%s)'
            '<div class="catdesc">%s</div></li>'
            % (category.name, category.name, len(category.packages),
                category.description)
        for category in categories]) +
        '\n</ul>\n')

    total = len(categories)
    stats = sidebox('Portage',
            htmltext('There are %d portage categories.' % total))
    return page('Portage Categories', [htmltext(body), stats])


def meta_category(_, name):
    """/portage/<meta>/"""
    cat_factory = portage.CategoryFactory(database)
    nlen = len(name)
    # get categories for this meta-category
    categories = [category for category in cat_factory.get()
        if category.name[:nlen + 1] == name + '-']

    pkg_factory = portage.PackageFactory(database)
    for category in categories:
        category.set_packages(pkg_factory.get(category.name))

    body = ('<h3 class="title">The "%s" Metagory:</h3><ul '
        'class="categoryList">\n' % name +
        '\n'.join(['<li><a href="%s/">%s</a> (%s)<br /> %s</li>'
        %  (
            category.name,
            category.name,
            len(category.packages),
            category.description
            )
        for category in categories]) +
        '\n</ul>\n')

    total = len(categories)
    stats = sidebox('Portage Meta Category: %s' % name,
            htmltext('There are %d "%s" categories.' % (total, name)))
    return page('Portage Meta Category "%s"' % name, [htmltext(body), stats])

def _q_lookup(request, component):
    """/portage/<category>|<meta>/
    basically multiplexes btw meta_category() and Category()"""
    if '-' in component:
        return Category(request, component)
    else:
        # this is like a meta-category.  I made this up on my own
        # (nothing to do with a portage structure), but basically it's
        # the set off all categories with the same prefix (before the '-')
        return meta_category(request, component)



class Category:
    """/portage/<category>/"""
    _q_exports = []

    def __init__(self, _, component):
        self.name = component
        pkg_factory = portage.PackageFactory(database)
        categories = portage.CategoryFactory(database).get()
        for category in categories:
            if category.name == self.name:
                self.category = category
                break

        self.packages = [pkg_factory.create(self.name, pkg.name)
            for pkg in pkg_factory.get(self.name)]

    def _q_index(self, _):
        """index"""
        body = ('<h3 class="title">The "%s" Category</h3>'
            '<ul class="packageList">\n' % self.name +
                '\n'.join(['<li><a href="%s/">%s</a><div class="catdesc">'
                    '%s</div></li>' % (pkg.name, pkg.name,
                html_quote(pkg.description))
                for pkg in self.packages])
                + '</ul>'
        )
        total = len(self.packages)
        stats = sidebox(self.name , htmltext(self.category.description +
            '<p>There are %d packages in this category.</p>'
            % total))
        return page('Packages in %s' % self.name, [htmltext(body), stats])

    def _q_lookup(self, request, component):
        """Request particular package"""
        return Package(request, component)

class Package:
    """/porgage/<category>/<package>/"""
    #image = None
    _q_exports = ['homepage', 'changelog', 'bugs', 'forums', 'brief',
        ('image.png', 'image')]

    def __init__(self, request, component):
        self.name = component
        self.category = request.get_path().split('/')[-3]
        pkg_factory = portage.PackageFactory(database)
        self.package = pkg_factory.create(self.category, self.name)
        self.ebuilds = portage.EbuildFactory(database).get(self.category,
            self.name)
        self.licenses = set()
        for pkg_ebuild in self.ebuilds:
            self.licenses = self.licenses.union(pkg_ebuild.licenses)

# TODO: Remove if no longer needed
##    def _q_index_old(self, request):
##        data = """\
##Package name is %s<br />
##Category name is %s<br />
##""" % (self.name, self.category)
##
##        sb1 = """\
##<a href="homepage">Home Page</a><br />
##<a href="changelog">Changelog</a><br />
##<a href="bugs">Bugs</a><br />
##<a href="forums">Forums</a><br />
##"""
##        s = []
##        for eb in self.ebuilds:
##            s.append('<a href="%s/">%s</a>' % (eb.version, eb.version))
##
##        sb2 = '<br />'.join(s)
##
##        sb1 = sidebox(self.name, htmltext(sb1))
##        sb2 = sidebox('Releases', htmltext(sb2))
##        return page('Package: %s' % self.name, [htmltext(data), sb1 + sb2])

    def brief(self, _):
        """Brief info about package"""
        return page(
            'The %s Package' % (self.name),
            [package.brief(self.package), package.sidebox(self.package)
                + '\n' + ebuild.licenses(self)
                + '\n' + package.ebuilds(self.package, database)
            ]
        )

    _q_index = brief

    # TODO: implement detail()
    def _q_lookup(self, request, component):
        """Return a particular ebuild"""
        return Ebuild(request, component)

    def homepage(self, _):
        """Redirect to package's home page"""
        return redirect(self.package.homepages[0])

    def changelog(self, _):
        """Redirect to package's changelog"""
        return redirect('http://sources.gentoo.org/viewcvs.py/'
            '*checkout*/%s/%s/ChangeLog'
            % (self.category, self.name))

    def bugs(self, _):
        """Redirect to bugzilla search using package as keyword"""
        url = ('http://bugs.gentoo.org/buglist.cgi?query_format=&'
                'short_desc_type=allwords&short_desc=%s&bug_status='
                'UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status='
                'REOPENED' % self.name)
        return redirect(url)

    def forums(self, _):
        """Redirect to forums.gentoo.org search using package as keyword"""
        url = ('http://forums.gentoo.org//search.php?search_terms=all&'
                'show_results=topics&search_keywords=%s&mode=results'
                % self.name)

        return redirect(url)

    def image(self, request):
        """Return package image if it exists else return PACKAGE_IMAGE_DEFAULT"""
        image_path = '%s/%s/%s.jpg' % (config.PACKAGE_IMAGE_DIR,
                self.category, self.name)

        print image_path
        if exists(image_path):
            graphic = StaticFile(image_path, mime_type = 'image/png')
        else:
            print config.PACKAGE_IMAGE_DEFAULT
            graphic = StaticFile(config.PACKAGE_IMAGE_DEFAULT)

        return graphic(request)

class Ebuild:
    """/portage/<category>/<package>/<version>/"""
    _q_exports = ['brief']

    def __init__(self, request, component):
        self.version = component
        self.category, self.name = request.get_path().split('/')[-4:-2]
        self.ebuild = portage.EbuildFactory(database).get(self.category,
                self.name, self.version)[0]

    def brief(self, _):
        """Brief info about the ebuild"""
        return page(
            'Ebuild for %s %s' % (self.name, self.version),
            [ebuild.brief(self.ebuild), ebuild.sidebox(self.ebuild)
                + '\n' + ebuild.licenses(self.ebuild)
                + '\n' + ebuild.others(self.ebuild, database)
            ]
        )
        #return ebuild.brief(self.ebuild)

    _q_index = brief

    # TODO: implement detail()
    def detail(self, request):
        """Detailed info about ebuild"""
        return self.brief(request)
