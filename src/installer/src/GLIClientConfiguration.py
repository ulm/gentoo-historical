class GLIClientConfiguration:
	architecture_template = None
	profile_server_uri = ""
	
	# This contains a list of all the install steps completed
	# It is used for dependency checking
	install_steps_completed = []
	
	# This allows InstallTemplate to communicate back to the controller
	# The controller can poll this information to inform the user
	# This gives a percentange of the step that is completed
	current_step_percent = 0
	# This is a string describing what the step is currently doing
	current_step_process_desc = ""
