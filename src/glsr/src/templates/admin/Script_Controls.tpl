      <form name="script_control_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="script">

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

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_all_categories" value="Modify Categories" />
           </td>

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_add_new_cat" value="Add Category" />
           </td>

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_all_languages" value="Modify Languages" />
           </td>

           <td height="40" valign="center" class="" nowrap>&nbsp;&nbsp;
           <input type="submit" class="button" name="show_add_new_lang" value="Add Language" />
           </td>
                                 
          </tr>
          </table>
         </td>
	</tr>
      </table>
      <br />

      </form>
