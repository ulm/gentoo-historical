
      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}
      
      <table width="90%" class="standard_table">
        <tr>
          <td class="header">Script Management Controls</td>
          <td class="header" align="right" valign="middle"></td>
        </tr>
	<tr>
          <td colspan="2" height="40" valign="center" class="standard_cell">
          <table border="0" cellspacing="0" cellpadding="0">
          <tr>

	<form name="script_control_form" method="GET" action="index.py">
	<input type="hidden" name="page" value="script">
          
           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           {IF TOTAL_SCRIPTS == 0}
           <input type="submit" class="button" name="list_all_scripts" value="List All Scripts" />
           {ELSE}
           <input type="submit" class="button" name="" value="Hide Script List" />
           {!IF}
           </td>

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="open_search_page" value="Search Scripts" />
           </td>

	</form>

	<form name="script_control_form" method="GET" action="index.py">
	<input type="hidden" name="page" value="category">

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_all" value="Modify Categories" />
           </td>

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_add" value="Add Category" />
           </td>

	</form>

	<form name="script_control_form" method="GET" action="index.py">
	<input type="hidden" name="page" value="language">

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_all" value="Modify Languages" />
           </td>

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_add" value="Add Language" />
           </td>

	</form>

          </tr>
          </table>
         </td>
	</tr>
      </table>
      <br />

