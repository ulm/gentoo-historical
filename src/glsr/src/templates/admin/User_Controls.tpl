      <form name="user_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="user">

      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}
      
      <table width="90%" class="standard_table">
        <tr>
          <td class="header">User Management Controls</td>
          <td class="header" align="right" valign="middle"><img src="{GLSR_URL}images/people.png" width="48" height="48" /></td>
        </tr>
	<tr>
          <td colspan="2" height="40" valign="middle" class="standard_cell">
          <table border="0" cellspacing="0" cellpadding="0">
          <tr>
          
           <td height="40" valign="center" class="">&nbsp;&nbsp;
          {IF TOTAL_USERS == 0}
          <input type="submit" class="button" name="show_all_users" value="List All Users" />
          {ELSE}
          <input type="submit" class="button" name="" value="Hide User List" />
          {!IF}
          </td>

          <td height="40" valign="center" class="">&nbsp;&nbsp;
          <input type="submit" class="button" name="show_add_new_user" value="Add New User" />
          </td>
          </tr>
          </table>
         </td>
	</tr>
      </table>
      <br />

      {IF WARN_MESSAGE != ""}
      <font class="warn_message">{WARN_MESSAGE}</font><br /><br />
      {!IF}
      
      {IF TOTAL_USERS > 0}
      <!-- Listing of all users in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="9" class="header">User Listing</td>
        </tr>

        <tr>
          <td class="sub_header">Alias</td>
          <td class="sub_header">Full Name</td>
          <td class="sub_header">Email Address</td>
	  <td class="sub_header">Type</td>
	  <td class="sub_header">Rank</td>
          <td class="sub_header">Joined</td>
          <td class="sub_header">Last IP</td>
          <td class="sub_header" align="center">Delete</td>
        </tr>
        {LOOP USER_LOOP}
	<tr>
          <td class="standard_row_{USER_LOOP.row}"><a href="index.py?page=user&show_modify_user={USER_LOOP.user_id}">{USER_LOOP.user_alias}</a></td>
          <td class="standard_row_{USER_LOOP.row}">{USER_LOOP.user_fullname}</td>
          <td class="standard_row_{USER_LOOP.row}">{USER_LOOP.user_email}</td>
          <td class="standard_row_{USER_LOOP.row}">
{IF USER_LOOP.type == 3}Admin{!IF}{IF USER_LOOP.user_type == 1}Developer{ELSE}User{!IF}</td>
          <td class="standard_row_{USER_LOOP.row}">{USER_LOOP.user_rank}</td>
          <td class="standard_row_{USER_LOOP.row}">{USER_LOOP.user_joined}</td>
          <td class="standard_row_{USER_LOOP.row}">{USER_LOOP.user_lastip}</td>
          <td class="standard_row_{USER_LOOP.row}" align="center"><input type="checkbox" name="delete" value="{USER_LOOP.user_id}" /></td>
	</tr>
        {!LOOP}
        <tr>
          <td class="standard_cell" colspan="9" align="right"><input type="submit" class="button" name="delete_users" value="Delete" />&nbsp;&nbsp;</td>
        </tr>
      </table>
      {!IF}

      {IF MODIFY_USER != 0}
      <!-- The form to add a new user or modify an existing one -->
      <input type="hidden" name="uid" value="{MODIFY_USER}" />
      <table width="45%" class="standard_table">
        <tr>
          <td colspan="" class="header">{IF ADD_USER_FORM == 1}Add New User{ELSE}Modify User{!IF}</td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Alias:</font><br />
           <input type="text" class="text" name="alias" value="{ALIAS}" maxlength="25" />
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Full Name:</font><br />
           <input type="text" class="text" name="fullname" value="{FULLNAME}" maxlength="40" />
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Email:</font><br />
           <input type="text" class="text" name="email" value="{EMAIL}" maxlength="50" />
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Type:</font><br />
           <select name="type" class="dropdown">
            <option value="0">User</option>
            <option value="1" {IF TYPE == 1}selected{!IF}>Developer</option>
            <option value="3" {IF TYPE == 3}selected{!IF}>Administrator</option>
           </select>
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Password:</font><br />
           <input type="password" class="text" name="password1" maxlength="32" />
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Password Confirm:</font><br />
           <input type="password" class="text" name="password2" maxlength="32" />
          </td>
        </tr>
        <tr>
           <td class="standard_cell">
           <input type="submit" class="button" name="{IF ADD_USER_FORM == 1}add_new_user{ELSE}modify_user{!IF}" value="Save"/>
           </td>
        </tr>
      </table>
      {!IF}

      </form>
