# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = "$Id: error.py,v 1.1 2005/06/06 19:22:59 hadfield Exp $"
__modulename__ = "error"

class GLSRError(Exception):
    """The base error class for GLSR."""
    pass

class InvalidAction(GLSRError):
    """Raised when an invalid action is passed to a domain page."""
    pass
