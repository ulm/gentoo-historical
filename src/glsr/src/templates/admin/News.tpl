      <form name="news_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="news">
           
      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}

      <table width="90%" class="standard_table">
        <tr>
          <td class="header">News Announcement Controls</td>
          <td class="header" align="right" valign="middle"><img src="{GLSR_URL}images/news.png" width="48" height="48" />
	</tr>
        <tr>
          <td colspan="2" height="40" valign="middle" class="standard_cell">
          <table border="0" cellspacing="0" cellpadding="0">
          <tr>

          <td height="40" valign="center" class="">&nbsp;&nbsp;
          {IF TOTAL_ANNOUNCE == 0}
          <input type="submit" class="button" name="show_all_announce" value="List All Announcements" />
          {ELSE}
          <input type="submit" class="button" name="" value="Hide Announcement List" />
          {!IF}
          </td>

	  <td height="40" valign="center" class="">&nbsp;&nbsp;
	  <input type="submit" class="button" name="show_add_new_announce" value="Make Announcement" />
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

      {IF TOTAL_ANNOUNCE > 0}
      <!-- Listing of all announcements in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="9" class="header">Announcement Listing</td>
        </tr>

	<tr>
          <td class="sub_header">ID</td>
          <td class="sub_header">Subject</td>
          <td class="sub_header">Created</td>
	  <td class="sub_header">Author</td>
          <td class="sub_header" align="center">Delete</td>
        </tr>
        {LOOP ANNOUNCE_LOOP}
        <tr>
          <td class="standard_row_{ANNOUNCE_LOOP.row}"><a href="index.py?page=news&show_modify_announce={ANNOUNCE_LOOP.news_id}">{ANNOUNCE_LOOP.news_id}</a></td>
	  <td class="standard_row_{ANNOUNCE_LOOP.row}">{ANNOUNCE_LOOP.news_subject}</td>
          <td class="standard_row_{ANNOUNCE_LOOP.row}">{ANNOUNCE_LOOP.news_date}</td>
          <td class="standard_row_{ANNOUNCE_LOOP.row}">{ANNOUNCE_LOOP.news_author_id}</td>
          <td class="standard_row_{ANNOUNCE_LOOP.row}" align="center"><input type="checkbox" name="delete" value="{ANNOUNCE_LOOP.news_id}" /></td>
	</tr>
        {!LOOP}
        <tr>
          <td class="standard_cell" colspan="9" align="right"><input type="submit" class="button" name="delete_announce" value="Delete" />&nbsp;&nbsp;</td>     
	</tr>
      </table>
      {!IF}

      {IF ADD_MODIFY_ANNOUNCE != 0}
      <!-- The form to add a new announcement or modify an existing one -->
      <input type="hidden" name="annid" value="{ADD_MODIFY_ANNOUNCE}" />
      <table width="45%" class="standard_table">
        <tr>
          <td colspan="" class="header">{ANNOUNCE_MODE}</td>
        </tr>                                
        <tr>
          <td class="standard_cell">
           <font class="instructional">Subject:</font><br />
           <input type="text" class="text-long" name="subject" value="{SUBJECT}" />
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Announcement:</font><br />
           <textarea rows="15" cols="50" class="text" name="announcement">{ANNOUNCEMENT}</textarea>
          </td>
        </tr>
        <tr>
           <td class="standard_cell">
           <input type="submit" class="button" name="{IF ADD_ANNOUNCE_FORM == 1}add_new_announce{ELSE}modify_announce{!IF}" value="Save"/>
           </td>
        </tr>
      </table>
      {!IF}

      </form>
