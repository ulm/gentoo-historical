#!/usr/bin/php -q
<?php /* $Id: runfrank.php,v 1.2 2003/03/18 21:57:52 klieber Exp $ */
/**
 * Frank
 *
 * The Gentoo mirror checking script
 *
 * @version $Revision: 1.2 $
 * @author A.Sleep <a.sleep@asleep.net>
 * @copyright (c) 2003 A.Sleep/Gentoo - GPL Version 2.0
 */

/**
 * Configure Options Follow
 */

/**
 * The path to the image root including final /
 */
$cfg['ImagePath'] = 'http://www.gentoo.org/images/';

/**
 * Output filename
 */
$cfg['OutputFile'] = '${WEBROOT}/dyn/mirrorhealth.xml';
#$cfg['OutputFile'] = './mirrorhealth.xml';

/**
 * The Red image
 */
$cfg['RedImage'] = 'red.gif';

/**
 * The Yellow image
 */
$cfg['YellowImage'] = 'yellow.gif';

/**
 * The Green image
 */
$cfg['GreenImage'] = 'green.gif';

/**
 * Hostlist for non-rsync mirrors
 * (full path or relative from current location)
 */
$cfg['HostList']  = './list';

/**
 * Header file (to use with output)
 */
$cfg['Header'] = './f_header.xml';

/**
 * Footer file (to use with output)
 */
$cfg['Footer'] = './f_footer.xml';

/**
 * Timestamp file in distfiles
 */
$cfg['DistfileTimestamp'] = 'distfiles/timestamp.chk';

/**
 * The RSYNC Path to the timestamp file
 */
$cfg['RsyncTimestamp'] = 'gentoo-portage/metadata/timestamp.chk';

/**
 * Location of the temp file when doing an ftp-based check
 */
$cfg['TempFile'] = '/tmp/ts.chk';

/*
 * * *  END of Configurable Options  * * *
 */

// debug setting
if (isset($argv[1]) and $argv[1] == 'debug') {
  define('DEBUG', true);
  error_reporting(E_ALL);
  echo "Running Frank in debug mode... mooo...\n";
}
else {
  define('DEBUG', false);
}

/*
 * Loads Frank
 */
require_once './Frank.php';

if (substr(date('Z'), 0, 1) == '-') {
  $utcTime = date('U')-substr(date('Z'), 1);
}
else {
  $utcTime = (date('U')+date('Z'));
}

/*
 * Holds the current date in GMT unix_timestamp
 */
define('NOW', $utcTime);

/*
 * Put together list of distfile hosts (http/ftp)
 */
if (!file_exists($cfg['HostList'])) {
  echo "The HostList does not exist: ",$cfg['HostList'],"\nExiting...\n";
  exit;
}
$distMirrors = @file($cfg['HostList']);
$i = 0;
foreach ($distMirrors as $thisDHost) {
  $distMirrors[$i] =& trim($thisDHost);
  $i++;
}

unset($thisDHost);

/*
 * Put together list of portage hosts (rsync)
 */
$rsyncHosts = array();
@exec('host rsync.gentoo.org', $rsyncHosts);
$i = 0;
foreach ($rsyncHosts as $thisRHost) {
  $bits = explode(' ', $thisRHost);
  $rsyncHosts[$i] = 'rsync://'.trim($bits[(count($bits)-1)]).'/';
  $i++;
}
unset($bits);
unset($thisRHost);

$mirrors = array_merge($rsyncHosts, $distMirrors);

asort($mirrors);

$i = 0;
foreach ($mirrors as $thisMirror) {

  $Frank =& new Frank($thisMirror);

  if (!$Frank->isAlive()) {
    $mirrorStatus[$i]['img'] =& $cfg['RedImage'];
  }
  else {
    $mirrorStatus[$i]['img'] = $cfg['GreenImage'];
    $mirrorStatus[$i]['up2date'] = $Frank->fileCheck();
  }

  if (!isset($mirrorStatus[$i]['up2date'])) {
    $mirrorStatus[$i]['up2date'] =& $cfg['RedImage'];
  }

  if (!isset($mirrorStatus[$i]['img'])) {
    $mirrorStatus[$i]['img'] =& $cfg['RedImage'];
  }

  $mirrorStatus[$i]['host']   = $Frank->host();
  $mirrorStatus[$i]['scheme'] = $Frank->scheme();
  if ($Frank->scheme() == 'http' or $Frank->scheme() == 'ftp') {
    $mirrorStatus[$i]['file'] = $Frank->path().$Frank->checkFile();
  }
  else {
    $mirrorStatus[$i]['file'] = null;
  }
  $i++;
}

/*
 * DONE
 * Start parsing for output
 */

// Suckup the templates and build the body
$body = file_get_contents($cfg['Header']);
foreach ($mirrorStatus as $thisStatus) {
  if (DEBUG) {
    echo "Building row for ",$thisStatus['host'],"...\n";
  }
  $body .= '<tr><ti>'.$thisStatus['host'].'</ti><ti><figure link="'.$cfg['ImagePath'].$thisStatus['img'].'" width="10" height="10" /></ti><ti><figure link="'.$thisStatus['up2date'].'" width="10" height="10" /></ti><ti>['.$thisStatus['scheme'].']</ti></tr>
';
}
$body .= file_get_contents($cfg['Footer']);

$body = str_replace('{LastUpdate}', date('r'), $body);

if (DEBUG) {
  echo "Starting to output ",$cfg['OutputFile'],"\n";
}

if (!$fp = fopen($cfg['OutputFile'], 'w')) {
  echo "WARNING: Could not open ",$cfg['OutputFile'],"!\n";
  exit;
}

if (!fwrite($fp, $body)) {
  echo "WARNING: Could not write ",$cfg['OutputFile'],"!\n";
  exit;
}

fclose($fp);
if (DEBUG) {
  echo "Done...\n";
}
exit;
// what are you looking down here for?
?>
