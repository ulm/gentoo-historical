      
      <form name="category_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="category">
      
      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}
      
      {IF WARN_MESSAGE == 1}
      <font class="warn_message">No Categories Found</font><br /><br />
      {!IF}
      
      {IF TOTAL > 0}
      <!-- Listing of all users in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="4" class="header">Category Listing</td>
        </tr>

        <tr>
          <td class="sub_header">Name</td>
          <td class="sub_header">Description</td>
          <td class="sub_header">Parent</td>
          <td class="sub_header" align="center">Delete</td>
        </tr>
        {LOOP MAIN_LOOP}
	<tr>
          <td class="standard_row_{MAIN_LOOP.row}" style="padding-left: {MAIN_LOOP.padding}px"><a href="index.py?page=category&show_modify={MAIN_LOOP.category_id}&mod_categories=Modify+Catgories">{MAIN_LOOP.category_name}</a></td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.category_descr}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{IF MAIN_LOOP.parent_name == "None"}Root Category{ELSE}{MAIN_LOOP.parent_name}{!IF}</td>
          <td class="standard_row_{MAIN_LOOP.row}" align="center"><input type="checkbox" name="delete_btn" value="{MAIN_LOOP.category_id}" /></td>
	</tr>
        {!LOOP}
        <tr>
          <td class="standard_cell" colspan="9" align="right"><input type="submit" class="button" name="delete" value="Delete" />&nbsp;&nbsp;</td>
        </tr>
      </table>
      {!IF}

      {IF MODIFY != 0}
      <!-- The form to add or modify categories -->
      <input type="hidden" name="category_id" value="{MODIFY}" />
      <table width="45%" class="standard_table">
        <tr>
          <td colspan="" class="header">{IF ADD_FORM == 1}Add New Catgory{ELSE}Modify Category{!IF}</td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Name:</font><br />
           <input type="text" class="text" name="name" value="{NAME}" />
          </td>
        </tr>
        <tr>
          <td class="standard_cell">
           <font class="instructional">Parent:</font><br />
           <select name="parent_id" class="dropdown">
	   <option value="0">None</option>
           {LOOP PARENT_LOOP}
             <option value="{PARENT_LOOP.category_id}" {IF PARENT_LOOP.category_name == PARENT}selected{!IF}>{PARENT_LOOP.category_name}</option>
           {!LOOP}
           </select>
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
           <input type="submit" class="button" name="{IF ADD_FORM == 1}add{ELSE}modify{!IF}" value="Save"/>
           </td>
        </tr>
      </table>
      {!IF}

      </form>
      