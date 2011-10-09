# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 1.1 $
# Date: $Date: 2011/10/09 00:38:43 $
# Copyright: This module has been placed in the public domain.

"""
Gentoo Linux Enhancement Proposal (GLEP) Reader.
"""

__docformat__ = 'reStructuredText'


from docutils.readers import pep as pepsreader
from docutils.transforms import gleps, peps


class Reader(pepsreader.Reader):

    """Glep reader class with minor modifications to the pep reader."""

    supported = ('glep',)
    """Contexts this reader supports."""

    def get_transforms(self):
        """Parse headers for gleps, not peps."""
        transforms = pepsreader.Reader.get_transforms(self)
        transforms.remove(peps.Headers)
        transforms.append(gleps.GLEPHeaders)
        return transforms
