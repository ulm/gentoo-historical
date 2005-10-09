import GLIServerProfile
import handler

class Clients(handler.Handler):

	def showclients(self):
		content = """
		<h2>Clients</h2>
		<table width="100%" cellpadding="0" cellpadding="0">
		<tr>
		  <td><u>Name</u></td>
		  <td><u>MAC</u></td>
		  <td><u>Current IP</u></td>
		  <td><u>Post-install IP</u></td>
		  <td><u>Profile</u></td>
		  <td><u>Install progress</u></td>
		</tr>
		"""
		for client in self.shared_info.clients:
			client_info = [client['name'], client['mac'], 'N/A', client['ip'], client['profile'], 'N/A']
			if client['mac'] in self.shared_info.client_state:
				client_info[2] = self.shared_info.client_state[client['mac']]['ip']
				client_info[5] = self.shared_info.client_state[client['mac']]['install_status']
			content += """
			<tr>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			  <td>%s</td>
			</tr>
			""" % tuple(client_info)
		content += """
		</table>
		"""
		return self.wrap_in_template(content)

	def handle(self, path):
		paths = { '/showclients': self.showclients,
		        }
		return_content = paths[path]()
		return self.headers_out, return_content
