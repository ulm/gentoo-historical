      
      <form name="category_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="script">
      
      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}
      
      {IF WARN_MESSAGE == 1}
      <font class="warn_message">No Categories Found</font><br /><br />
      {!IF}
      
      {IF TOTAL_CATS > 0}
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
        {LOOP CAT_LOOP}
	<tr>
          <td class="standard_row_{CAT_LOOP.row}" style="padding-left: {CAT_LOOP.padding}px"><a href="index.py?page=script&show_modify_cat={CAT_LOOP.category_id}&mod_categories=Modify+Catgories">{CAT_LOOP.category_name}</a></td>
          <td class="standard_row_{CAT_LOOP.row}">{CAT_LOOP.category_descr}</td>
          <td class="standard_row_{CAT_LOOP.row}">{IF CAT_LOOP.parent_name == "None"}Root Category{ELSE}{CAT_LOOP.parent_name}{!IF}</td>
          <td class="standard_row_{CAT_LOOP.row}" align="center"><input type="checkbox" name="delete" value="{CAT_LOOP.category_id}" /></td>
	</tr>
        {!LOOP}
        <tr>
          <td class="standard_cell" colspan="9" align="right"><input type="submit" class="button" name="delete_cats" value="Delete" />&nbsp;&nbsp;</td>
        </tr>
      </table>
      {!IF}

      {IF MODIFY_CAT != 0}
      <!-- The form to add or modify categories -->
      <input type="hidden" name="catid" value="{MODIFY_CAT}" />
      <table width="45%" class="standard_table">
        <tr>
          <td colspan="" class="header">{IF ADD_CAT_FORM == 1}Add New Catgory{ELSE}Modify Category{!IF}</td>
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
           <select name="parent" class="dropdown">
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
           <input type="submit" class="button" name="{IF ADD_CAT_FORM == 1}add_new_cat{ELSE}modify_cat{!IF}" value="Save"/>
           </td>
        </tr>
      </table>
      {!IF}

      </form>
      