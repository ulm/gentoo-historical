      <form name="user_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="yourscripts">

      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}
      
      {IF WARN_MESSAGE == 1}
      <font class="warn_message">No Scripts Found</font><br /><br />
      {!IF}


      {IF TOTAL > 0}
      <!-- Listing of all your scripts in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="8" class="header">Script Listing</td>
        </tr>

        <tr>
          <td class="sub_header">Name</td>
          <td class="sub_header">Version</td>
          <td class="sub_header">Category</td>
	  <td class="sub_header">Rank</td>
          <td class="sub_header">Language</td>
          <td class="sub_header">Date</td>
          <td class="sub_header">Approved By</td>
          <td class="sub_header">Status</td>
        </tr>
        {LOOP MAIN_LOOP}
	<tr>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_name}&nbsp;</a></td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_version}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_category_id}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_rank}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_language_id}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_date}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_approvedby}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_approved}&nbsp;</td>
	</tr>
        {!LOOP}
      </table>
      {!IF}




      {IF MODIFY != 0}      
      <!-- The form to add a new script -->
      <input type="hidden" name="script_id" value="{MODIFY}" />
      <table width="45%" class="standard_table">
        <tr>
          <td colspan="" class="header">{IF ADD_FORM == 0}Add New Script{ELSE}Modify Script{!IF}</td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">Name:</font><br />
           <input type="text" class="text-long" name="name" value="{NAME}" />
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
           <font class="instructional">Category:</font><br />
           <select name="category_id">
             <option value="0">Select a Category</option>
             {LOOP CATEGORY_LOOP}
             <option value="{CATEGORY_LOOP.category_id}" {IF CATEGORY_LOOP.category_id == CATEGORY_ID}selected{!IF}>{CATEGORY_LOOP.category_name}</option>
             {!LOOP}
           </select>
          </td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Language:</font><br />
           <select name="language_id">
             <option value="0">Select a Language</option>
             {LOOP LANGUAGE_LOOP}
             <option value="{LANGUAGE_LOOP.language_id}" {IF LANGUAGE_LOOP.language_id == LANGUAGE_ID}selected{!IF}>{LANGUAGE_LOOP.language_name}</option>
             {!LOOP}
           </select>
          </td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Body:</font><br />
           <textarea rows="15" cols="50" class="text" name="body">{BODY}</textarea>
          </td>
        </tr>
        <tr>
           <td class="standard_cell">
           <input type="submit" class="button" name="{IF ADD_FORM == 1}add{ELSE}modify{!IF}" value="Save"/>
           </td>
        </tr>
      </table>
      {!IF}

      </form>
