<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>Gentoo Linux Script Repository</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link title="new" rel="stylesheet" href="{GLSR_URL}css/glsr.css" type="text/css">
<link REL="shortcut icon" HREF="{GLSR_URL}images/favicon.ico" TYPE="image/x-icon">
</head>
<body>
<table width="100%" height="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td align="left" valign="top" height="125"><table width="100%" height="125"  border="0" cellpadding="0" cellspacing="0" background="{GLSR_URL}images/header-bk.png">
      <tr>
        <td><img src="{GLSR_URL}images/glogo.png" width="193" height="125"><img src="{GLSR_URL}images/splogo-beta.png" width="350" height="125"></td>
      </tr>
    </table></td>
  </tr>
  <tr>
    <td height="25" align="left" valign="center" bgcolor="#000000"><span class="menu">
      <a class="menulink" href="index.py?page=main">Main</a> |
      <a class="menulink" href="index.py?page=news">News</a> |
      <a class="menulink" href="index.py?page=script_search&list_all=True">View Scripts</a> |
      <a class="menulink" href="index.py?page=script_search">Search</a> |
      <a class="menulink" href="index.py?page=memberlist">Member List</a>
      {IF USER_ALIAS != ""}
      | <a class="menulink" href="index.py?page=profile">Profile</a>
      | <a class="menulink" href="index.py?page=script_search&search_submitter_id={USER_ID}">View Your Scripts</a> 
      | <a class="menulink" href="index.py?page=create_script&show_add=True">Create New Script</a> 
      | <a class="menulink" href="index.py?page=logout">Logout [{USER_ALIAS}]</a>
      {ELSE}
      | <a class="menulink" href="index.py?page=login">Login</a>
      {!IF}
      
    </span></td>
  </tr>
  <tr>
   <td align="center" valign="top">
    <br>

