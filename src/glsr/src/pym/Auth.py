# Copyright 2004 Ian Leitch
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#
# $Id: Auth.py,v 1.1.1.1 2004/06/04 06:38:34 port001 Exp $
#

__modulename__ = "Auth"

def GenMd5(passwd):
    """Generate hex md5 digest for given password"""

    import md5

    md5obj = md5.new()
    md5obj.update(passwd)
    
    return md5obj.hexdigest()	



