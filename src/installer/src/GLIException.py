"""
Gentoo Linux Installer

$Id: GLIException.py,v 1.4 2004/08/25 19:38:10 samyron Exp $
Copyright 2004 Gentoo Technologies Inc.

GLIException is the base class for all of the exceptions
raised by the installer.
"""

class GLIException(Exception):
	error_levels = ['notice', 'warning', 'fatal']

	def __init__(self, error_level, function_name, error_msg):
		if error_level not in GLIException.error_levels:
			raise NoSuchErrorLevelException('fatal', '__init__', "No such error level: %s" % error_level)

		Exception.__init__(self, error_level, function_name, error_msg)

	def get_function_name(self):
		return self.args[1]

	def get_error_level(self):
		return self.args[0]

	def get_error_msg(self):
		return self.args[2]

	def __str__(self):
		return repr("%s: %s: %s" % (self.args[0], self.args[1], self.args[2]))

class IPAddressError(GLIException):
	pass

class NoSuchFileError(GLIException):
	pass

class InstallProfileError(GLIException):
	pass

class MountError(GLIException):
	pass

class CopyError(GLIException):
	pass

class Stage1Error(GLIException):
	pass

class Stage2Error(GLIException):
	pass

class URIError(GLIException):
	pass

class InterfaceError(GLIException):
	pass

class DefaultGatewayError(GLIException):
	pass

class PasswordError(GLIException):
	pass

class NetworkInterfacesError(GLIException):
	pass

class PartitionTableError(GLIException):
	pass

class DefaultGatewayError(GLIException):
	pass

class EthDeviceError(GLIException):
	pass

class InputError(GLIException):
	pass

class UnpackTarballError(GLIException):
	pass

class DependencyError(GLIException):
	pass

class InstallTemplateError(GLIException):
	pass

class DHCPError(GLIException):
	pass

class SetIPError(GLIException):
	pass

class DefaultRouteError(GLIException):
	pass

class SSHError(GLIException):
	pass

class KernelModuleError(GLIException):
	pass

class KernelModulesError(GLIException):
	pass

class KernelConfigURIError(GLIException):
	pass

class KernelInitRDError(GLIException):
	pass

class CronDaemonPKGError(GLIException):
	pass

class LoggingDaemonPKGError(GLIException):
	pass

class BootLoaderMBRError(GLIException):
	pass

class BootLoaderPkgError(GLIException):
	pass

class KernelBootsplashError(GLIException):
	pass

class KernelSourcePKGError(GLIException):
	pass

class UserError(GLIException):
	pass

class UsersError(GLIException):
	pass

class RootPassHashError(GLIException):
	pass

class TimeZoneError(GLIException):
	pass

class StageTarballURIError(GLIException):
	pass

class CustomStage3TarballURIError(GLIException):
	pass

class InstallStageError(GLIException):
	pass

class PortageTreeSyncError(GLIException):
	pass

class PortageTreeSnapshotURIError(GLIException):
	pass

class DomainnameError(GLIException):
	pass

class HostnameError(GLIException):
	pass

class NISDomainnameError(GLIException):
	pass

class MakeConfError(GLIException):
	pass

class RCConfError(GLIException):
	pass

class IgnoreInstallStepDepends(GLIException):
	pass

class InstallRP_PPPOE(GLIException):
	pass

class FileSystemTools(GLIException):
	pass

class InstallPcmciaCS(GLIException):
	pass

class DnsServersError(GLIException):
	pass

class NoSuchErrorLevelException(GLIException):
	pass

