      
      <form name="language_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="script">
      
      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}
      
      {IF WARN_MESSAGE == 1}
      <font class="warn_message">No Languages Found</font><br /><br />
      {!IF}
      
      {IF TOTAL_LANGS > 0}
      <!-- Listing of all users in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="4" class="header">Language Listing</td>
        </tr>

        <tr>
          <td class="sub_header">Name</td>
          <td class="sub_header">Description</td>
          <td class="sub_header" align="center">Delete</td>
        </tr>
        {LOOP LANG_LOOP}
	<tr>
          <td class="standard_row_{LANG_LOOP.row}"><a href="index.py?page=script&show_modify_lang={LANG_LOOP.language_id}">{LANG_LOOP.language_name}</a></td>
          <td class="standard_row_{LANG_LOOP.row}">{LANG_LOOP.language_descr}</td>
          <td class="standard_row_{LANG_LOOP.row}" align="center"><input type="checkbox" name="delete" value="{LANG_LOOP.language_id}" /></td>
	</tr>
        {!LOOP}
        <tr>
          <td class="standard_cell" colspan="9" align="right"><input type="submit" class="button" name="delete_langs" value="Delete" />&nbsp;&nbsp;</td>
        </tr>
      </table>
      {!IF}

      {IF MODIFY_LANG != 0}
      <!-- The form to add or modify languages -->
      <input type="hidden" name="langid" value="{MODIFY_LANG}" />
      <table width="45%" class="standard_table">
        <tr>
          <td colspan="" class="header">{IF ADD_LANG_FORM == 1}Add New Language{ELSE}Modify Language{!IF}</td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Name:</font><br />
           <input type="text" class="text" name="name" value="{NAME}" />
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Description:</font><br />
           <input type="text" class="text-long" name="descr" value="{DESCR}" />
          </td>
        </tr>
        <tr>
           <td class="standard_cell">
           <input type="submit" class="button" name="{IF ADD_LANG_FORM == 1}add_new_lang{ELSE}modify_lang{!IF}" value="Save"/>
           </td>
        </tr>
      </table>
      {!IF}

      </form>
      