"""/stats/
Like /licenses/ this is only a redirector. Redirect to bugzilla.
"""
from quixote import redirect

_q_exports = []

SBASE = 'http://cia.navi.cx/stats/author/'

def _q_index(_):
    """This should never be called"""
    return redirect(SBASE)

def _q_lookup(_, component):
    """Redirect: component should be a bug number"""
    return redirect('%s%s' % (SBASE, component))
