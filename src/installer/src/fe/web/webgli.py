#!/usr/bin/python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.



def index():
	import sys
	sys.path.append("/home/codeman/installer/src")
	import ClientConfig
#import Partitioning
#import NetworkMounts
#import Stage
#import PortageTree
#import ConfigFiles
#import Kernel
#import GLIGenDialog somehow.
	data = "<html><body><table><tr><td width=200>" #Outer Table + top row + top left box
	data += "Picture here. Gentoo Logo</td>"
	data += "<td><img src=\"banner-800x64.png\"></td></tr>\n"
	#Lefthand column of steps.
	data += "<tr><td valign=\"top\">"
	data += "<p><a href=\"webgli.py\">Welcome</a></p>\n"
	data += "<p><a href=\"webgli.py?page=ClientConfig\">Client Config</a></p>\n"
	data += "<p><a href=\"webgli.py?page=Partitioning\">Partitioning</a></p>\n"
	data += "<p><a href=\"webgli.py?page=NetworkMounts\">Network Mounts</a></p>\n"
	data += "<p><a href=\"webgli.py?page=Stage\">Stage Selection</a></p>\n"
	data += "<p><a href=\"webgli.py?page=PortageTree\">Portage Tree</a></p>"
	data += "<p><a href=\"webgli.py?page=ConfigFiles\">Config Files</a></p>"
	data += "<p><a href=\"webgli.py?page=Kernel\">Kernel</a></p>"
	data += "<p><a href=\"webgli.py?page=Bootloader\">Bootloader</a></p>"
	data += "<p><a href=\"webgli.py?page=Timezone\">Timezone</a></p>"
	data += "<p><a href=\"webgli.py?page=Networking\">Networking</a></p>"
	data += "<p><a href=\"webgli.py?page=Daemons\">Daemons</a></p>"
	data += "<p><a href=\"webgli.py?page=ExtraPackages\">Extra Packages</a></p>"
	data += "<p><a href=\"webgli.py?page=Users\">Users</a></p>"
	data += "<p><a href=\"webgli.py?page=Review\">Review</a></p>\n"
	data += "</td>"
	#Now for the main content
	data += "<td>\n"
	data += show_main_content()
	data += "</td></tr></table></body></html>"
	return data

def show_welcome():
	print "Welcoming string here.<BR>"
	print "LOCAL INSTALL ASSUMED FOR THIS FRONT END<br>"


def show_main_content():

	page = ""
#	if 'page' in self.post_params and self.post_params['page']:
#		page = self.post_params['page']
	if page == "ClientConfig":
		data = ClientConfig.show_client_config(data)
	elif page == "Partitioning":
		data = Partitioning.show_partitioning()
	elif page == "NetworkMounts":
		data = NetworkMounts.show_networkmounts()
	elif page == "Stage":
		data = Stage.show_stage()
	elif page == "PortageTree":
		data = PortageTree.show_portage_tree()
	elif page == "ConfigFiles":
		data = ConfigFiles.show_config_files()
	elif page == "Kernel":
		data = Kernel.show_kernel()
	elif page == "Bootloader":
		data = Bootloader.show_bootloader()
	elif page == "Timezone":
		data = Timezone.show_timezone()
	elif page == "Networking":
		data = Networking.show_networking()
	elif page == "Daemons":
		data = Daemons.show_daemons()
	elif page == "ExtraPackages":
		data = ExtraPackages.show_extra_packages()
	elif page == "Users":
		data = Users.show_users()
	elif page == "Review":
		data = Review.show_review()
	else:
		data = show_welcome()	

	import ClientConfig
	data = ClientConfig.show_client_config()
	return data
