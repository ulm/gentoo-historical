<?

def show_portage_tree(self):
  	#import some stuff
  	print '<form name="PortageTree" method="post" action="webgli.php?page=ConfigFiles">'
	print 'Portage selection string here: <br>'
	print 'Portage Tree Sync Type: <br><input type="radio" name="SyncType" value="sync">Normal. Use emerge sync RECOMMENDED!<br>'
	print '<input type="radio" name="SyncType" value="webrsync">HTTP daily snapshot. Use when rsync is firewalled.<br>'
	print '<input type="radio" name="SyncType" value="snapshot">Use a portage snapshot, either a local file or a URL<br>'
	print '<input type="radio" name="SyncType" value="none">Extra cases such as if /usr/portage is an NFS mount<br>'
	#if not snapshot then grey out box.
	print '<hr>If using a snapshot, enter the snapshot URI: <input type="text" name="SnapshotURI" value="" length="80"><br>'
	
  	#Print buttons for Next/Previous/Help/Save
	print "<hr><table><tr>"
	print '<td><input name="Load" type="button" value="Load"></td>'
	print '<td><input name="Save" type="button" value="Save"></td>'
	print '<td><input name="Help" type="button" value="Help"></td>'
	print '<td><input name="Previous" type="button" value="Previous"></td>'
	print '<td><input name="Next" type="button" value="Next"></td></tr></table>'
	print "</form>"

?>
