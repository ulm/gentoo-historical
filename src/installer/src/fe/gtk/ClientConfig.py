import gtk
import GLIScreen
import GLIUtility

class Panel(GLIScreen.GLIScreen):

	title = "Client Configuration (pre-install setup)"

	def __init__(self, controller):
		GLIScreen.GLIScreen.__init__(self, controller)
		vert = gtk.VBox(False, 0)
		vert.set_border_width(10)

		content_str = """On this screen, you will set all your pre-install options such as networking,
		chroot directory, logfile location, architecture, etc."""

		content_label = gtk.Label(content_str)
		vert.pack_start(content_label, expand=False, fill=False, padding=5)

		self.notebook = gtk.Notebook()

		basicbox = gtk.VBox(False, 0)
		basicbox.set_border_width(10)
		hbox = gtk.HBox(False, 0)
		tmplabel = gtk.Label()
		tmplabel.set_markup("<b><u>Network setup (for install only):</u></b>")
		hbox.pack_start(tmplabel, expand=False, fill=False, padding=0)
		basicbox.pack_start(hbox, expand=False, fill=False, padding=0)
		hbox = gtk.HBox(False, 0)
		hbox.pack_start(gtk.Label("Interface:"), expand=False, fill=False, padding=0)
		self.interface_combo = gtk.combo_box_entry_new_text()
		self.interface_combo.get_child().set_width_chars(9)
		self.interface_combo.connect("changed", self.interface_changed)
		self.interfaces = GLIUtility.get_eth_devices()
		for device in self.interfaces:
			self.interface_combo.append_text(device)
		hbox.pack_start(self.interface_combo, expand=False, fill=False, padding=10)
		basicbox.pack_start(hbox, expand=False, fill=False, padding=7)
		hbox = gtk.HBox(False, 0)
		self.basic_dhcp_radio = gtk.RadioButton(label="DHCP")
		self.basic_dhcp_radio.connect("toggled", self.dhcp_static_toggled, "dhcp")
		hbox.pack_start(self.basic_dhcp_radio, expand=False, fill=False, padding=0)
		basicbox.pack_start(hbox, expand=False, fill=False, padding=0)
		hbox = gtk.HBox(False, 0)
		self.basic_static_radio = gtk.RadioButton(group=self.basic_dhcp_radio, label="Static")
		self.basic_static_radio.connect("toggled", self.dhcp_static_toggled, "static")
		hbox.pack_start(self.basic_static_radio, expand=False, fill=False, padding=0)
		basicbox.pack_start(hbox, expand=False, fill=False, padding=3)
		hbox = gtk.HBox(False, 0)
		tmptable = gtk.Table(rows=5, columns=1)
		tmptable.set_col_spacings(6)
		tmptable.set_row_spacings(5)
		tmptable.attach(gtk.Label("        "), 0, 1, 0, 1)
		tmplabel = gtk.Label("IP address:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 1, 2, 0, 1)
		self.ip_address_entry = gtk.Entry()
		self.ip_address_entry.set_width_chars(20)
		tmptable.attach(self.ip_address_entry, 2, 3, 0, 1)
		tmptable.attach(gtk.Label("        "), 3, 4, 0, 1)
		tmplabel = gtk.Label("Netmask:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 4, 5, 0, 1)
		self.netmask_entry = gtk.Entry()
		self.netmask_entry.set_width_chars(20)
		tmptable.attach(self.netmask_entry, 5, 6, 0, 1)
		tmplabel = gtk.Label("Broadcast:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 1, 2, 1, 2)
		self.broadcast_entry = gtk.Entry()
		self.broadcast_entry.set_width_chars(20)
		tmptable.attach(self.broadcast_entry, 2, 3, 1, 2)
		tmplabel = gtk.Label("Gateway:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 4, 5, 1, 2)
		self.gateway_entry = gtk.Entry()
		self.gateway_entry.set_width_chars(20)
		tmptable.attach(self.gateway_entry, 5, 6, 1, 2)
		tmplabel = gtk.Label("DNS servers:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 1, 2, 2, 3)
		self.dns_entry = gtk.Entry()
		self.dns_entry.set_width_chars(20)
		tmptable.attach(self.dns_entry, 2, 3, 2, 3)
		hbox.pack_start(tmptable, expand=False, fill=False, padding=0)
		basicbox.pack_start(hbox, expand=False, fill=False, padding=3)
		hbox = gtk.HBox(False, 0)
		tmptable = gtk.Table(rows=5, columns=2)
		tmptable.set_col_spacings(6)
		tmptable.set_row_spacings(5)
#		tmptable.attach(gtk.Label("   "), 0, 2, 0, 1)
		tmplabel = gtk.Label()
		tmplabel.set_markup("<b><u>Proxies:</u></b>")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 2, 1, 2)
		tmplabel = gtk.Label("HTTP Proxy:")
		tmplabel.set_alignment(0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 2, 3)
		self.http_proxy_entry = gtk.Entry()
		tmptable.attach(self.http_proxy_entry, 1, 2, 2, 3)
		tmplabel = gtk.Label("FTP Proxy:")
		tmplabel.set_alignment(0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 3, 4)
		self.ftp_proxy_entry = gtk.Entry()
		tmptable.attach(self.ftp_proxy_entry, 1, 2, 3, 4)
		tmplabel = gtk.Label("Rsync Proxy:")
		tmplabel.set_alignment(0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 4, 5)
		self.rsync_proxy_entry = gtk.Entry()
		tmptable.attach(self.rsync_proxy_entry, 1, 2, 4, 5)
		hbox.pack_start(tmptable, expand=False, fill=False, padding=0)
		basicbox.pack_start(hbox, expand=False, fill=False, padding=3)
		self.notebook.append_page(basicbox, gtk.Label("Networking"))

		advbox = gtk.VBox(False, 0)
		advbox.set_border_width(10)
		hbox = gtk.HBox(False, 0)
		tmptable = gtk.Table(rows=5, columns=1)
		tmptable.set_col_spacings(6)
		tmptable.set_row_spacings(5)
		tmplabel = gtk.Label()
		tmplabel.set_markup("<b><u>Directories and logfiles:</u></b>")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 2, 0, 1)
		tmplabel = gtk.Label("Chroot directory:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 1, 2)
		self.chroot_dir_entry = gtk.Entry()
		self.chroot_dir_entry.set_width_chars(25)
		tmptable.attach(self.chroot_dir_entry, 1, 2, 1, 2)
		tmplabel = gtk.Label("Logfile:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 2, 3)
		self.logfile_entry = gtk.Entry()
		self.logfile_entry.set_width_chars(25)
		tmptable.attach(self.logfile_entry, 1, 2, 2, 3)
		tmplabel = gtk.Label("   ")
		tmptable.attach(tmplabel, 0, 1, 3, 4)
		tmplabel = gtk.Label()
		tmplabel.set_markup("<b><u>SSH:</u></b>")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 2, 4, 5)
		tmplabel = gtk.Label("Start SSHd:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 5, 6)
		tmphbox = gtk.HBox(False, 0)
		self.sshd_yes_radio = gtk.RadioButton(label="Yes")
		tmphbox.pack_start(self.sshd_yes_radio, expand=False, fill=False, padding=0)
		self.sshd_no_radio = gtk.RadioButton(group=self.sshd_yes_radio, label="No")
		tmphbox.pack_start(self.sshd_no_radio, expand=False, fill=False, padding=15)
		tmptable.attach(tmphbox, 1, 2, 5, 6)
		tmplabel = gtk.Label("Root password:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 6, 7)
		self.root_password_entry = gtk.Entry()
		self.root_password_entry.set_width_chars(25)
		self.root_password_entry.set_visibility(False)
		tmptable.attach(self.root_password_entry, 1, 2, 6, 7, xoptions=0)
		tmplabel = gtk.Label("Verify root password:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 7, 8)
		self.verify_root_password_entry = gtk.Entry()
		self.verify_root_password_entry.set_width_chars(25)
		self.verify_root_password_entry.set_visibility(False)
		tmptable.attach(self.verify_root_password_entry, 1, 2, 7, 8, xoptions=0)
		tmplabel = gtk.Label("   ")
		tmptable.attach(tmplabel, 0, 1, 8, 9)
		tmplabel = gtk.Label()
		tmplabel.set_markup("<b><u>Kernel modules:</u></b>")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 2, 9, 10)
		tmplabel = gtk.Label("Modules:")
		tmplabel.set_alignment(0.0, 0.5)
		tmptable.attach(tmplabel, 0, 1, 10, 11)
		self.modules_entry = gtk.Entry()
		self.modules_entry.set_width_chars(25)
		tmptable.attach(self.modules_entry, 1, 2, 10, 11)

		hbox.pack_start(tmptable, expand=False, fill=False, padding=0)
		advbox.pack_start(hbox, expand=False, fill=False, padding=0)
		self.notebook.append_page(advbox, gtk.Label("Misc."))

		vert.pack_start(self.notebook, expand=True, fill=True, padding=0)

		self.add_content(vert)

	def interface_changed(self, combobox):
		hw_addr, ip_addr, mask, bcast, gw, up = ("", "", "", "", "", "")
		interface = combobox.child.get_text()
		try:
			if interface.startswith("eth"):
				hw_addr, ip_addr, mask, bcast, gw, up = GLIUtility.get_eth_info(interface[-1:])
		except:
			pass
		self.ip_address_entry.set_text(ip_addr)
		self.netmask_entry.set_text(mask)
		self.broadcast_entry.set_text(bcast)
#		self.gateway_entry.set_text(gw)

	def dhcp_static_toggled(self, radiobutton, data=None):
		if radiobutton.get_active():
			# This one was just toggled ON
			if data == "dhcp":
				self.ip_address_entry.set_sensitive(False)
				self.netmask_entry.set_sensitive(False)
				self.broadcast_entry.set_sensitive(False)
				self.gateway_entry.set_sensitive(False)
				self.dns_entry.set_sensitive(False)
			else:
				self.ip_address_entry.set_sensitive(True)
				self.netmask_entry.set_sensitive(True)
				self.broadcast_entry.set_sensitive(True)
				self.gateway_entry.set_sensitive(True)
				self.dns_entry.set_sensitive(True)

	def activate(self):
		self.controller.SHOW_BUTTON_EXIT    = True
		self.controller.SHOW_BUTTON_HELP    = True
		self.controller.SHOW_BUTTON_BACK    = False
		self.controller.SHOW_BUTTON_FORWARD = True
		self.controller.SHOW_BUTTON_FINISH  = False

		interface = self.controller.client_profile.get_network_interface()
		ip = self.controller.client_profile.get_network_ip()
		if not interface:
			self.interface_combo.set_active(0)
		else:
			self.interface_combo.child.set_text(interface)
			for i, dev in enumerate(self.interfaces):
				if dev == interface:
					self.interface_combo.set_active(i)
		if ip == "dhcp" or not ip:
			self.basic_dhcp_radio.set_active(True)
			self.dhcp_static_toggled(self.basic_dhcp_radio, "dhcp")
		else:
			self.basic_static_radio.set_active(True)
		self.chroot_dir_entry.set_text(self.controller.client_profile.get_root_mount_point())
		self.logfile_entry.set_text(self.controller.client_profile.get_log_file())
		if self.controller.client_profile.get_enable_ssh():
			self.sshd_yes_radio.set_active(True)
		else:
			self.sshd_no_radio.set_active(True)
		dns_servers = GLIUtility.spawn(r"grep -e '^nameserver' /etc/resolv.conf | sed -e 's:^nameserver ::'", return_output=True)[1].strip().split('\n')
		dns_servers = " ".join(dns_servers)
		self.dns_entry.set_text(dns_servers)
		self.gateway_entry.set_text(GLIUtility.spawn(r"/sbin/route -n | grep -e '^0\.0\.0\.0' | sed -e 's:^0\.0\.0\.0 \+::' -e 's: \+.\+$::'", return_output=True)[1].strip())
		self.modules_entry.set_text(" ".join(self.controller.client_profile.get_kernel_modules()))

	def deactivate(self):
		self.controller.client_profile.set_network_interface(None, self.interface_combo.get_child().get_text(), None)
		if self.basic_dhcp_radio.get_active():
			self.controller.client_profile.set_network_type(None, "dhcp", None)
		else:
			self.controller.client_profile.set_network_type(None, "static", None)
			self.controller.client_profile.set_network_ip(None, self.ip_address_entry.get_text(), None)
			self.controller.client_profile.set_network_netmask(None, self.netmask_entry.get_text(), None)
			self.controller.client_profile.set_network_broadcast(None, self.broadcast_entry.get_text(), None)
			self.controller.client_profile.set_network_gateway(None, self.gateway_entry.get_text(), None)
			self.controller.client_profile.set_dns_servers(None, self.dns_entry.get_text(), None)
		self.controller.client_profile.set_http_proxy(None, self.http_proxy_entry.get_text(), None)
		self.controller.client_profile.set_ftp_proxy(None, self.ftp_proxy_entry.get_text(), None)
		self.controller.client_profile.set_rsync_proxy(None, self.rsync_proxy_entry.get_text(), None)
		self.controller.client_profile.set_root_mount_point(None, self.chroot_dir_entry.get_text(), None)
		self.controller.client_profile.set_log_file(None, self.logfile_entry.get_text(), None)
		self.controller.client_profile.set_enable_ssh(None, self.sshd_yes_radio.get_active(), None)
		if self.root_password_entry.get_text() == self.verify_root_password_entry.get_text():
			self.controller.client_profile.set_root_passwd(None, GLIUtility.hash_password(self.root_password_entry.get_text()), None)
		self.controller.client_profile.set_kernel_modules(None, self.modules_entry.get_text(), None)
		self.controller.cc.set_configuration(self.controller.client_profile)
		self.controller.cc.start_pre_install()
				
		return True
