<?php /* $Id: Frank.php,v 1.1 2003/03/18 21:56:06 klieber Exp $ */
/**
 * Frank
 *
 * The Gentoo mirror checking class
 *
 * @version $Revision: 1.1 $
 * @author A.Sleep <a.sleep@asleep.net>
 * @copyright (c) 2003 A.Sleep for Gentoo - GPL Version 2.0
 * @access public
 */

class Frank {

  /**
   * @var string
   * @access private
   */
  var $_mirror;

  /**
   * @var array
   * @access private
   */
  var $_ma;

  /**
   * @var string
   * @access private
   */
  var $_file;

  /**
   * @var string
   * @access private
   */
  var $_ftpTmpFile;

  /**
   * @var string
   * @access private
   */
  var $_rsyncPath;

  /**
   * @var string
   * @access private
   */
  var $_red;

  /**
   * @var string
   * @access private
   */
  var $_yellow;

  /**
   * @var string
   * @access private
   */
  var $_green;

  function Frank($mirror)
  {
    global $cfg;

    // don't ask...
    $this->_file       =& $cfg['DistfilesTimestamp'];
    $this->_rsyncPath  =& $cfg['RsyncTimestamp'];
    $this->_ftpTmpFile =& $cfg['TempFile'];
    $this->_red        =& $cfg['RedImage'];
    $this->_yellow     =& $cfg['YellowImage'];
    $this->_green      =& $cfg['GreenImage'];
    $this->_mirror     = trim($mirror);

    $this->_parseBits();
    unset($mirror);

    if (DEBUG) {
      echo "Checking ",$this->host(),"\n";
    }
  }


  /**
   * Wrapper for parse_url
   *
   * @access private
   */

  function _parseBits()
  {
    $this->_ma = parse_url($this->_mirror);
  }


  /**
   * Returns true if _file exists on $this->host()
   *
   * @return bool
   * @access public
   */

  function fileCheck()
  {
    if (substr($this->path(), -1) != '/') {
      $this->_slashPath();
    }
    if ($this->scheme() == 'ftp') {
      return $this->_checkFtp();
    }
    else if ($this->scheme() == 'http') {
      return $this->_checkHttp();
    }
    else if ($this->scheme() == 'rsync') {
      return $this->_checkRsync();
    }
    else {
      return false;
    }
  }


  /**
   * Does an FTP-style filecheck
   *
   * @return bool
   * @access private
   */

  function _checkFtp()
  {

    if (!$_cid = ftp_connect($this->host())) {
      return $this->_red;
    }

    if (!$_lr = @ftp_login($_cid, 'anonymous', 'frank@gentoo.org')) {
      return $this->_red;
    }

    if (!@ftp_get($_cid, $this->_ftpTmpFile, $this->path().$this->checkFile(), FTP_ASCII)) {
      return $this->_red;
    }

    $file = file_get_contents($this->_ftpTmpFile);

    @unlink($this->_ftpTmpFile);

    return $this->fileTime(trim($file));
  }


  /**
   * Does an HTTP-style filecheck
   *
   * @return bool
   * @access private
   */

  function _checkHttp()
  {
    if (!$file = @file_get_contents($this->_mirror.$this->checkfile())) {
      return $this->_red;
    }
    return $this->fileTime(trim($file));
  }


  /**
   * Does an rsync-style filecheck
   *
   * @return bool
   * @access private
   */

  function _checkRsync()
  {
    if (file_exists($this->_ftpTmpFile)) {
      @unlink($this->_ftpTmpFile);
    }
    if (DEBUG) {
      echo "doing rsync check on ",$this->host(),"\n";
    }
    @exec('rsync --timeout=10 '.$this->host().'::'.$this->_rsyncPath.' '.$this->_ftpTmpFile);
    if (!$file = @file_get_contents($this->_ftpTmpFile)) {
      return $this->_red;
    }
    if (!file_exists($this->_ftpTmpFile)) {
      return $this->_red;
    }
    return $this->fileTime(trim($file));
  }


  /**
   * Returns bool if time in file is within correct params.
   *
   * @return bool
   * @access public
   */

  function fileTime($file)
  {
    //    $remoteTime = strtotime('Mon,  3 Mar 2003 23:58:19 +0000');
    $remoteTime = strtotime($file);
    if (DEBUG) {
      echo "file time: $remoteTime\n";
    }

    //    $remoteTime = strtotime($file);
    //    $localTime  = gmdate('U');
    if (DEBUG) {
      echo "current time: ",NOW,"\n";
    }

    $_portageTimes   = array(1801,3601);
    $_distfilesTimes = array(14401,28802);

    $diff = (NOW-$remoteTime);
    if (DEBUG) {
      echo "diff: $diff\n";
    }

    if ($this->scheme() == 'http' or $this->scheme() == 'ftp') {
      if ($diff <= $_distfilesTimes[0]) {
	if (DEBUG) {
	  echo "diff is <= $_distfilesTimes[0]\n";
	}
	return $this->_green;
      }
      if ($diff <= $_distfilesTimes[1]) {
	if (DEBUG) {
	  echo "diff is <= $_distfilesTimes[1]\n";
	}
	return $this->_yellow;
      }
      if (DEBUG) {
	echo "diff was larger then $_distfilesTimes[0] and $_distfilesTimes[1].\n";
      }
      return $this->_red;
    }
    else if ($this->scheme() == 'rsync') {
      if ($diff <= $_portageTimes[0]) {
	if (DEBUG) {
	  echo "diff is <= $_portageTimes[0]\n";
	}
	return $this->_green;
      }
      if ($diff >= $_portageTimes[1]) {
	if (DEBUG) {
	  echo "diff is <= $_portageTimes[1]\n";
	}
	return $this->_yellow;
      }
      if (DEBUG) {
	echo "diff was larger then $_portageTimes[0] and $_portageTimes[1].\n";
      }
      return $this->_red;
    }
  }


  /**
   * Adds a final slash to this mirrors path
   *
   * @access private
   */

  function _slashPath()
  {
    $this->_mirror     = $this->_mirror.'/';
    $this->_ma['path'] = $this->_ma['path'].'/';
  }


  /**
   * Returns the scheme of this mirror
   *
   * @return string
   * @access public
   */

  function & scheme()
  {
    return $this->_ma['scheme'];
  }


  /**
   * Returns the file to be checked for
   *
   * @return string
   * @access public
   */

  function & checkfile()
  {
    return $this->_file;
  }


  /**
   * Returns the host of this mirror
   *
   * @return string
   * @access puclic
   */

  function & host()
  {
    return $this->_ma['host'];
  }


  /**
   * Returns the path of this mirror
   *
   * @return string
   * @access public
   */

  function & path()
  {
    return $this->_ma['path'];
  }


  /**
   * Checks the host to see if it's responding
   * Nice with $this->scheme of course
   *
   * @return bool
   * @access public
   */

  function isAlive()
  {
    if ($this->scheme() == 'http') {
      $_port = 80;
    }
    else if ($this->scheme() == 'ftp') {
      $_port = 21;
    }
    else {
      return 'Unsupported Scheme '.$this->scheme();
    }

    if (!$fp = @fsockopen($this->host(), $_port, $_errno, $_errstr, 30)) {
      return false;
    }

    @fclose($fp);
    return true;
  }

}

?>
