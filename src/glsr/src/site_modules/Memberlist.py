# Copyright 2004 Ian Leitch
# Copyright 2004 Scott Hadfield
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Memberlist.py,v 1.2 2005/01/25 22:21:08 hadfield Exp $
#

import Config
from SiteModule import SiteModule
from User import User

__modulename__ = 'Memberlist'

class Memberlist(SiteModule):

    def init(self):

        self._template = Config.Template['memberlist']

    def _set_params(self):

        items_per_page = 49
        
        # Get our list of memebers
        user_obj = User()
        member_loop = user_obj.List()
        for member in member_loop:
            member.update({"script_count": 1})

        start = int(self._req.Values.getvalue("start", 0))
        
        member_loop = self._sort(member_loop)
        
        (page_loop, current_page) = \
                    self._pages(member_loop, start, items_per_page)
        member_loop = member_loop[start:start + items_per_page]

        self._tmpl.param("GLSR_URL", Config.URL)
        self._tmpl.param("CURRENT_PAGE", current_page)
        self._tmpl.param("NEXT_START", start + items_per_page)
        self._tmpl.param("PAGE_LOOP", page_loop, "loop")
        self._tmpl.param("PAGE_LOOP_LEN", len(page_loop))
        self._tmpl.param("MEMBER_LOOP", self._sort(member_loop), "loop")

    def _pages(self, list_in, start, items_per_page):

        page_list = [{"page": 1, "start": 0}]

        for i in range(items_per_page, len(list_in), items_per_page):
            page_list.append({"page": i/items_per_page + 1, "start": i})

        current_page = start/items_per_page + 1
        return page_list, current_page
    
    def _sort(self, list_in):
        """Sorts the list

        The list is sorted by using the sortby and order form parameters if the
        'sort' submit button was pressed.
        """

        rows = list(list_in)

        def cmpfunca(x, y):
            if x[sortby] > y[sortby]:
                return 1
            elif x[sortby] < y[sortby]:
                return -1
            return 0
        
        def cmpfuncd(x, y):
            if x[sortby] < y[sortby]:
                return 1
            elif x[sortby] > y[sortby]:
                return -1
            return 0
        
        sortby = self._req.Values.getvalue('sortby', "")
        order = self._req.Values.getvalue('order', "a")
        if order != 'd': order = 'a'
        self._tmpl.param("SORTBY", sortby)
        self._tmpl.param("ORDER", order)

        if self._req.Values.getvalue('sort') == None:
            return rows

        rows.sort(eval("cmpfunc" + order))

        return rows
        
    def display(self):

        self._set_params()
        self._tmpl.compile(self._template)
        return self._tmpl
