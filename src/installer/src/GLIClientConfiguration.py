class GLIClientConfiguration:

	SHARED_CLIENT_CONFIGURATION = None

	def shared_client_configuration(cls):
		if GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION == None:
			GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION = cls()

		return GLIClientConfiguration.SHARED_CLIENT_CONFIGURATION

	def __init__(self):
		self._architecture_template = None
		self._profile_server_uri = ""
	
		# This contains a list of all the install steps completed
		# It is used for dependency checking
		self._install_steps_completed = []
	
		# This allows InstallTemplate to communicate back to the controller
		# The controller can poll this information to inform the user
		# This gives a percentange of the step that is completed
		self._current_step_percent = 0
		# This is a string describing what the step is currently doing
		self._current_step_process_desc = ""

		# This is the full path to the logfile
		self._log_file = "/var/log/installer.log"
		
		# Current process temporary log (for parsing)
		self._proc_temp_log = "/tmp/proc.tmp.log"

		# This is the root mount point
		self._root_mount_point = "/mnt/gentoo"

	def get_architecture_template(self):
		return self._architecture_template
	
	def set_architecture_template(self, architecture_template):
		self._architecture_template = architecture_template
	
	def get_profile_server_uri(self):
		return self._profile_server_uri
	
	def set_profile_server_uri(self, profile_server_uri):
		self._profile_server_uri = profile_server_uri

	def get_install_steps_completed(self):
		return self._install_steps_completed
	
	def set_install_steps_completed(self, install_steps_completed):
		self._install_steps_completed = install_steps_completed

	def get_current_step_percent(self):
		return self._current_step_percent
	
	def set_current_step_percent(self, current_step_percent):
		self._current_step_percent = current_step_percent

	def get_current_step_process_desc(self):
		return self._current_step_process_desc
	
	def set_current_step_process_desc(self, current_step_process_desc):
		self._current_step_process_desc = current_step_process_desc

	def get_log_file(self):
		return self._log_file
	
	def set_log_file(self, log_file):
		self._log_file = log_file

	def get_proc_temp_log(self):
		return self._proc_temp_log
	
	def set_proc_temp_log(self, proc_temp_log):
		self._proc_temp_log = proc_temp_log

	def get_root_mount_point(self):
		return self._root_mount_point
	
	def set_root_mount_point(self, root_mount_point):
		self._root_mount_point = root_mount_point

	shared_client_configuration = classmethod(shared_client_configuration)
