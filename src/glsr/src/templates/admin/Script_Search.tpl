      <form name="script_search_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="script">
           
      <table width="600px" class="standard_table">
        <tr>
          <td class="header">Script Search</td>
          <td class="header" align="right" valign="middle">&nbsp;</td>
	</tr>
	<tr>
	  <td colspan="2" valign="middle" class="standard_cell">
            <table border="0" width="550px" cellspacing="0" cellpadding="0">
            <tr>
             <td class="standard_cell">
               <font class="instructional">Script Name:</font>
             </td>
             <td>
               <input type="text" class="text-long" name="name" value="" />
             </td>
            </tr>
            <tr>
              <td valign="middle" class="standard_cell">
                <font class="instructional">Description:</font>
              </td>
              <td>
                <input type="text" class="text-long" name="descr" value="" />
              </td>
            </tr>
            <tr>
              <td valign="middle" class="standard_cell">
                <font class="instructional">Submitter:</font>
              </td>
              <td>
                <input type="text" class="text-long" name="submitter" value="" />
              </td>
            </tr>
            <tr>
              <td colspan="2" nowrap class="standard_cell" valign="middle">
                <input type="checkbox" class="checkbox" name="most_recent" checked />&nbsp;&nbsp;Find only the latest versions of scripts.
              </td>
            </tr>
            </table>
          </td>
	</tr>
        <tr>
          <td colspan="2" bgcolor="#dddaec" valign="bottom"><hr /></td>
        </tr>        
        <tr>
     	  <td colspan="2" valign="middle" class="standard_cell">
          <table border="0" width="550px" cellspacing="0" cellpadding="0">
          <tr>
            <td colspan="2" class="standard_cell"><font class="instructional">Language:</font></td>
            <td class="standard_cell"><font class="instructional">Category:</font></td>
            <td class="standard_cell"><font class="instructional">Status:</font></td>
          </tr>
          <tr>
            <td nowrap class="standard_cell" width="1%" valign="top">
              <input type="checkbox" class="checkbox" name="lang_perl" />Perl <br />
              <input type="checkbox" class="checkbox" name="lang_python" />Python <br />
              <input type="checkbox" class="checkbox" name="lang_ruby" />Ruby <br />
              <input type="checkbox" class="checkbox" name="lang_php" />PHP <br />
              <input type="checkbox" class="checkbox" name="lang_javascript" />Java Script <br />
            </td>
            <td nowrap class="standard_cell" valign="top">
              <input type="checkbox" class="checkbox" name="lang_bash" />Bash <br />
              <input type="checkbox" class="checkbox" name="lang_java" />Java <br />
              <input type="checkbox" class="checkbox" name="lang_c" />C/C++ <br />
              <input type="checkbox" class="checkbox" name="lang_html" />HTML <br />
              <input type="checkbox" class="checkbox" name="lang_other" />Other <br />
            </td>
   
            <td nowrap class="standard_cell" valign="top">
              <input type="checkbox" class="checkbox" name="cat_portage" />Portage <br />
              <input type="checkbox" class="checkbox" name="cat_networking" />Networking <br />
              <input type="checkbox" class="checkbox" name="cat_laptop" />Laptops <br />
              <input type="checkbox" class="checkbox" name="cat_web" />Web <br />
              <input type="checkbox" class="checkbox" name="cat_other" />Other <br />
            </td>
            <td nowrap class="standard_cell" valign="top">
              <input type="checkbox" class="checkbox" name="stat_approved" />Approved <br />
              <input type="checkbox" class="checkbox" name="stat_pending" />Pending <br />
              <input type="checkbox" class="checkbox" name="stat_rejected" />Rejected <br />
            </td>
          </tr>
          </table>
          </td>
        </tr>
        <tr>
          <td colspan="2" bgcolor="#dddaec" valign="bottom"><hr /></td>
        </tr>
        <tr>
          <td colspan="2" class="standard_cell">
            <input type="submit" class="button" name="script_search" value="Search" /></td>
        </tr>
      </table>

      </form>
