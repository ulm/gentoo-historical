      <form name="user_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="yourscripts">

      {IF REPORT != ""}
        {IF REPORT_TYPE == "normal"}
          <font class="report_normal">
        {!F}
        {IF REPORT_TYPE == "warn"}
          <font class="report_warn">
        {!IF}
        {IF REPORT_TYPE == "fatal"}
          <font class="report_fatal">
        {!IF}
        {REPORT}
        </font><br /><br />
      {!IF}

      {IF TOTAL > 0}
      <!-- Listing of all your scripts in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="7" class="header">Script Listing</td>
        </tr>

        <tr>
          <td class="sub_header">Name</td>
          <td class="sub_header">Version</td>
          <td class="sub_header">Category</td>
	  <td class="sub_header">Rank</td>
          <td class="sub_header">Language</td>
          <td class="sub_header">Date</td>
          <td class="sub_header">Approved By</td>
          <!-- <td class="sub_header">Status</td> -->
        </tr>
        {LOOP MAIN_LOOP}
	<tr>
	  <!-- 012345678901234567 -->
          <td class="standard_row_{MAIN_LOOP.row}"><a href="index.py?page=yourscripts&show_parent=True&script_id={MAIN_LOOP.script_id}">{MAIN_LOOP.script_name}</a></td>
          <td class="standard_row_{MAIN_LOOP.row}"><a href="index.py?page=yourscripts&show_subscript=True&script_id={MAIN_LOOP.subscript_id}">{MAIN_LOOP.subscript_version}</a></td>

          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.category}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_rank}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.language}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_date}&nbsp;</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_approvedby}&nbsp;</td>
	</tr>
        {!LOOP}
      </table>
      {!IF}




      {IF MODIFY != 0}      
      <!-- The form to add a new script -->
      <input type="hidden" name="script_id" value="{MODIFY}" />
      <table width="90%" class="standard_table">
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
           <font class="instructional">Version (numeric):</font><br />
           <input type="text" class="text" name="version" value="{VERSION}" />
          </td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">Category:</font><br />
           <select name="category_id">
             <option value="0">Select a Category</option>
             {LOOP CATEGORY_LOOP}<!-- 012345678901234567 -->
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
             <!-- {LANGUAGE_LOOP.language_name} -->
             <option value="{LANGUAGE_LOOP.language_id}" {IF LANGUAGE_LOOP.language_id == LANGUAGE_ID}selected{!IF}>{LANGUAGE_LOOP.language_name}</option>
             {!LOOP}
           </select>
          </td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Body:</font><br />
           <textarea rows="15" style="width: 100%;" class="text" name="body">{BODY}</textarea>
          </td>
        </tr>
        <tr>
           <td class="standard_cell">
           <input type="submit" class="button" name="{IF ADD_FORM == 1}add{ELSE}modify{!IF}" value="Save" />
           </td>
        </tr>
      </table>
      {!IF}


      {IF SHOW_PARENT != 0}
      <br />
      <input type="hidden" name="show_modify" value="{PARENT_SCRIPT_ID}" />
      <input type="submit" class="button" name="" value="New Version" />
      {!IF}
      
      </form>
