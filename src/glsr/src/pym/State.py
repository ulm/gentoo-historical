# Copyright 2004-2005 Ian Leitch
# Copyright 2004-2005 Scott Hadfield
# Copyright 1999-2005 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
#

__revision__ = '$Id: State.py,v 1.5 2005/01/26 20:59:57 port001 Exp $'
__modulename__ = 'State'

ActiveThreads = 0

HTMLHeadersSent = False
HeaderTmplSent = False

ThisSession = None

UserDetial = None
Domain = None
Req = None
