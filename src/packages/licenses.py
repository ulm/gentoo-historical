"""/licences/ portion of site.  Basically redirects to cvs"""

from quixote import redirect

_q_exports = []

LBASE = 'http://www.gentoo.org/cgi-bin/viewcvs.cgi/*checkout*/licenses'

def _q_index(_):
    """This should never be called..."""
    # TODO:redirect elsewhere as LBASE is not accessible
    return redirect(LBASE)

def _q_lookup(_, component):
    """component will be a particular license"""
    return redirect('%s/%s' % (LBASE, component))
