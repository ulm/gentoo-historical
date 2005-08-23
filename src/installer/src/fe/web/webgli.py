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
	data += "<p><a href=\"webgli.php\">Welcome</a></p>\n"
	data += "<p><a href=\"webgli.php?page=ClientConfig\">Client Config</a></p>\n"
	data += "<p><a href=\"webgli.php?page=Partitioning\">Partitioning</a></p>\n"
	data += "<p><a href=\"webgli.php?page=NetworkMounts\">Network Mounts</a></p>\n"
	data += "<p><a href=\"webgli.php?page=Stage\">Stage Selection</a></p>\n"
	data += "<p><a href=\"webgli.php?page=PortageTree\">Portage Tree</a></p>"
	data += "<p><a href=\"webgli.php?page=ConfigFiles\">Config Files</a></p>"
	data += "<p><a href=\"webgli.php?page=Kernel\">Kernel</a></p>"
	data += "<p><a href=\"webgli.php?page=Bootloader\">Bootloader</a></p>"
	data += "<p><a href=\"webgli.php?page=Timezone\">Timezone</a></p>"
	data += "<p><a href=\"webgli.php?page=Networking\">Networking</a></p>"
	data += "<p><a href=\"webgli.php?page=Daemons\">Daemons</a></p>"
	data += "<p><a href=\"webgli.php?page=ExtraPackages\">Extra Packages</a></p>"
	data += "<p><a href=\"webgli.php?page=Users\">Users</a></p>"
	data += "<p><a href=\"webgli.php?page=Review\">Review</a></p>\n"
	data += "</td>"
	#Now for the main content
	data += "<td>\n"
	data = show_main_content(data)
	data += "</td></tr></table></body></html>"
	return data

def show_welcome():
	print "Welcoming string here.<BR>"
	print "LOCAL INSTALL ASSUMED FOR THIS FRONT END<br>"


def show_main_content(data):
	#$page = $_GET["page"];  How does python do HTTP vars?
	import ClientConfig
	data = ClientConfig.show_client_config(data)
	return data
	crap = """	switch($page)
	{
		case "ClientConfig":
			show_client_config();
			break;
		case "Partitioning":
			show_partitioning();
			break;
		case "NetworkMounts":
			show_networkmounts();
			break;
		case "Stage":
			show_stage();
			break;
		case "PortageTree":
			show_portage_tree();
			break;
		case "ConfigFiles":
			show_config_files();
			break;
		case "Kernel":
			show_kernel();
			break;
		case "Bootloader":
			show_bootloader();
			break;
		case "Timezone":
			show_timezone();
			break;
		case "Networking":
			show_networking();
			break;
		case "Daemons":
			show_daemons();
			break;
		case "ExtraPackages":
			show_extra_packages();
			break;
		case "Users":
			show_users();
			break;
		case "Review":
			show_review();
			break;
			
		default:
			show_welcome();
"""
