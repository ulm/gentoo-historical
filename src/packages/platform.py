"""This module handles the /updates, /new, and /bumps trees of the site.
For whatever reason, I have decided to call these "platforms" and "stable" and
"testing" are considered "branches" of that platform
"""
import re
from packages.config import ARCHLIST, DEFAULT_LIMIT
from quixote.html import htmltext
from packages.ui.main import page, sidebox
from packages.ui.ebuild import brief
from packages.ui.menu import do_menu

TIMEFRAME_RE = re.compile(r'([1-9][0-9]?)(hour|day|week)s?')
class Platform:
    """Specific platform

    This is a base class that is used to show pages dependent upon a platform
    and branch.  This class must be inherited and the .query() method overriden
    in order to be useful.  For an example see the UpdatesPlatform class in
    updates.py
    """

    _q_exports = ['stable', 'testing']

    def __init__(self, name, platform_name, description = None):
        """
        name: root name of the platform pages
        platform_name: this particular patform (e.g. "x86")
        There is a built-in html renderer, but it can be overriden. The
        default html renderer assumes items are ebuilds.

        description: text description of platform (for use in renderers)
        """

        self.name = name
        self.platform_name = platform_name
        self.description = description or name
        self.count = None
        self.timeframe = None

    def _q_index(self, request):
        """Main entry point for platforms"""
        return self.index(request, '')

    def _q_resolve(self, _):
        """NOT SURE WHY I PUT THIS HERE.  IS IT NECESSARY?"""
        #print component
        return self._q_index(self)

    def stable(self, request):
        """Stable-only"""
        return self.index(request, 'stable')

    def testing(self, request):
        """Testing-only"""
        return self.index(request, 'testing')

    def index(self, request, branch, timeframe = None):
        """The main index.
        timeframe can be passed to this tree, e.g. you are looking for updates
        within 1hour then ?timefram=1hour.  count is the maximum number of
        entries to report (your SQL LIMIT)
        format is what format you want the output in.  The default is HTML
        Any other format must have a render_<format>() method or else it
        defaults back to HTML.
        """
        count = None
        req_count = request.get_form_var('count', None)
        if req_count:
            try:
                req_count = int(req_count)
                self.count = req_count
            except ValueError:
                req_count = DEFAULT_LIMIT
        else:
            req_count = DEFAULT_LIMIT
        format = request.get_form_var('format', 'html')

        timeframe = request.get_form_var('timeframe', None)

        if timeframe:
            match = TIMEFRAME_RE.search(timeframe)

            if not match:
                timeframe = '3hours'

        self.timeframe = timeframe

        items = self.query(branch = branch, count = req_count,
            timeframe = timeframe)

        try:
            renderer = getattr(self, 'render_%s' % format)
        except AttributeError:
            renderer = self.render_html

        return renderer(items, branch)

    def render_html(self, items, branch):
        """Create HTML for the request"""
        # data used in string formatting
        data = {
            'name': self.name,
            'branch': branch,
            'platform_name': self.platform_name
        }
        if self.platform_name:
            data['extra'] = '/%s' % self.platform_name
        else:
            data['extra'] = ''
        #add misc. parameters
        misc = []
        if self.count:
            misc.append('count=%s' % self.count)
        if self.timeframe:
            misc.append('timeframe=%s' % self.timeframe)

        if misc:
            data['url_extra'] = '?' + '&'.join(misc)
        else:
            data['url_extra'] = ''

        branch_list = []
        update_list = []
        update_list.append(('Updates', '/updates%(extra)s/%(branch)s' % data,
            None, None))
        update_list.append(('New', '/new%(extra)s/%(branch)s' % data,
            None, None))
        update_list.append(('Bumps', '/bumps%(extra)s/%(branch)s' % data,
            None, None))

        branch_list.append(('stable','/%(name)s%(extra)s/stable%(url_extra)s'
            % data, None, '(+)'))
        branch_list.append(('testing','/%(name)s%(extra)s/testing%(url_extra)s'
            % data, None, '(~)'))
        branch_list.append(('either','/%(name)s%(extra)s/%(url_extra)s'
            % data, None, '(+/~)'))

        sideboxes = ['', '', '']
        if self.platform_name:
            sideboxes[1] = sidebox(self.platform_name, do_menu(branch_list))
            sideboxes[0] = sidebox('%s %s' % (self.platform_name, branch),
                do_menu(update_list))
        platform_summary = htmltext('<div class="summary">Gentoo is available '
            'on these platforms:</div>\n')
        platform_list = []
        for arch in ARCHLIST:
            url = "/%s/%s/" % (self.name, arch) + data['url_extra']
            platform_list.append((arch, url, None, None))
        platform_menu = do_menu(platform_list)
        sideboxes[2] = sidebox('platforms',  platform_summary + platform_menu)
        title = '%s for %s %s' % (self.description,
            (self.platform_name or 'Portage'), branch)

        if self.timeframe:
            factor, units = TIMEFRAME_RE.search(self.timeframe).groups()
            if factor == '1':
                title = '%s within the %s' % (title, units)
            else:
                title = '%s within the past %s %ss' % (title, factor, units)

        body = '<h3 class="title">%s</h3>\n' % title
        count = 0
        for item in items:
            body = '%s\n<div class="%s">%s</div>\n' % (body,
                ['even', 'odd'][count % 2], brief(item))
            count = count +  1
        return page(title, [htmltext(body), sideboxes[0] + sideboxes[1] +
            sideboxes[2]])

    def query(self, branch = '', count = DEFAULT_LIMIT, timeframe = None):
        """YOU NEED TO OVERRIDE THIS!"""
        branch, count, timeframe # to shut up pylint ;-)
        return []
