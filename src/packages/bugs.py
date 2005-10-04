"""/bugs/
Like /licenses/ this is only a redirector. Redirect to bugzilla.
"""
from quixote import redirect

_q_exports = []

BBASE = 'http://bugs.gentoo.org/show_bug.cgi'

def _q_index(_):
    """This should never be called"""
    return redirect(BBASE)

def _q_lookup(_, component):
    """Redirect: component should be a bug number"""
    return redirect('%s?id=%s' % (BBASE, component))
