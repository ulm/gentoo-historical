# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/embedded_target.py,v 1.7 2005/01/04 21:13:43 wolf31o2 Exp $

"""
This class works like a 'stage3'.  A stage2 tarball is unpacked, but instead
of building a stage3, it emerges a 'system' into another directory
inside the 'stage2' system.  This way we do not have to emerge gcc/portage
into the staged system.

It sounds real complicated but basically it runs
ROOT=/tmp/submerge emerge --blahblah foo bar
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_stage_target import *
from stat import *

class embedded_target(generic_stage_target):

    def __init__(self,spec,addlargs):
        self.required_values=[]
        self.valid_values=[]
        self.valid_values.extend(["embedded/empty","embedded/rm","embedded/unmerge","embedded/runscript","embedded/mergeroot","embedded/packages","embedded/use","embedded/fs-type"])

        if addlargs.has_key("embedded/fs-type"):
            self.valid_values.append("embedded/fs-ops")

        generic_stage_target.__init__(self,spec,addlargs)
	self.settings["image_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+"/image"	
               
    # taken from livecd-stage3 code
    def unmerge(self):
	    print "Unmerging packages"
            if self.settings.has_key("embedded/unmerge"):
		    if type(self.settings["embedded/unmerge"])==types.StringType:
			    self.settings["embedded/unmerge"]=[self.settings["embedded/unmerge"]]
		    myunmerge=self.settings["embedded/unmerge"][:]
                    
                    for x in range(0,len(myunmerge)):
                        myunmerge[x]="'"+myunmerge[x]+"'"
	     		myunmerge=string.join(myunmerge)
                    # before cleaning unmerge stuff
		    cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/unmerge.sh "+myunmerge,"unmerge script failed.")
                        
    def clean(self):
	    if self.settings.has_key("embedded/rm"):
		    if type(self.settings["embedded/rm"])==types.StringType:
			    self.settings["embedded/rm"]=[self.settings["embedded/rm"]]
			    print "Removing directories from image"
		    for x in self.settings["embedded/rm"]:
			    print "Removing "+x
			    os.system("rm -rf "+self.settings["chroot_path"]+"/tmp/mergeroot"+x)

    def build_fs(self):
        try:
            if self.settings.has_key("embedded/fs-type"):
                cmd("/bin/bash "+self.settings["sharedir"]+"/targets/embedded/embedded.sh package","filesystem packaging failed")
        except CatalystError:
                self.unbind()
                raise CatalystError, "embedded filesystem created aborting due to error."


    def run_local(self):
	    mypackages=list_bashify(self.settings["embedded/packages"])
	    print "Merging embedded image"
	    try:
		    cmd("/bin/bash "+self.settings["sharedir"]+"/targets/embedded/embedded.sh run")
	    except CatalystError:
		    self.unbind()
		    raise CatalystError, "Embedded build aborted due to error."
	    self.unmerge()
	    self.clean()
            self.build_fs()

    def set_action_sequence(self):
	self.settings["action_sequence"]=["dir_setup","unpack_and_bind","chroot_setup",\
					"setup_environment","run_local","unbind","capture"]
	
    def set_use(self):
        self.settings["use"]=self.settings["embedded/use"]
    def set_stage_path(self):
        self.settings["stage_path"]=self.settings["chroot_path"]+"/tmp/mergeroot"
	print "embedded stage path is "+self.settings["stage_path"]
def register(foo):
        foo.update({"embedded":embedded_target})
        return foo
