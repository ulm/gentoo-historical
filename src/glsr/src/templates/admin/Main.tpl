    <table width="90%" border="0" cellspacing="0" cellpadding="0" class="section_table">
      <tr>
        <td height="50" background="{GLSR_URL}images/header-bk.png">&nbsp;&nbsp;<span class="section_header_text">Scripts Pending Review</span></td><td width="50" height="50" align="center" valign="middle" background="{GLSR_URL}images/header-bk.png"><img src="{GLSR_URL}images/stock_notes.png" width="48" height="48"></td>
      </tr>
      <tr>
        <td height="30" colspan="2" class="stats_row_4"><span>&nbsp;&nbsp;No scripts pending review.</span></td>
      </tr>
    </table>
    <br />

    {IF ERROR_REPORTING != "False"}
    <form name="error_report_list" method="POST" action="index.py">
    <input type="hidden" name="page" value="main">
    <input type="hidden" name="domain" value="admin">

    <table width="90%" class="standard_table">
      <tr>
        <td colspan="3" class="header">Error Reports</td>
      </tr>
      <tr>
        <td class="sub_header">Date</td>
        <td class="sub_header">Module</td>
        <td class="sub_header">Error</td>
      </tr>
      {LOOP ERROR_REPORT_LIST}
      <tr>
        <td class="standard_row_{ERROR_REPORT_LIST.row}">{ERROR_REPORT_LIST.date}</td>
        <td class="standard_row_{ERROR_REPORT_LIST.row}">{ERROR_REPORT_LIST.module}</td>
        <td class="standard_row_{ERROR_REPORT_LIST.row}">{ERROR_REPORT_LIST.error}</td>
      </tr>
      {!LOOP}
      <tr>
         <td class="standard_cell" align="left"><a href="index.py?domain=admin&page=main&error_report_offset=all">Show all</a></td>
         <td class="standard_cell" colspan="3" align="right"><input type="submit" class="button" name="flush_error_reports" value="Flush Log" />&nbsp;&nbsp;</td>
      </tr>
    </table>
    </form>
    <br />
    {!IF}

    <form name="optimize_tables" method="POST" action="index.py">
    <input type="hidden" name="page" value="main">
    <input type="hidden" name="domain" value="admin">
    <table width="90%" class="standard_table">
      <tr>
        <td colspan="2" class="header">Table Optimization</td>
      </tr>
      <tr>
         <td class="standard_cell">Tables were last optimized on the {OPTIMIZE_DAYS}.</td>
         <td class="standard_cell" align="right"><input type="submit" class="button" name="optimize_tables" value="Optimize"></td>
      </tr>
    </table>
    </form>

    <table width="90%" class="standard_table">
     <tr>
      <td class="header" colspan="2">
       Who Is Online
      </td>
     </tr>
     <tr>
      <td class="standard_cell" colspan="2">
       There are currently {REGISTERED_SESSIONS_ONLINE_COUNT} users and {GUEST_SESSIONS_ONLINE} guests online.       
      </td>
     </tr>
     {IF REGISTERED_SESSIONS_ONLINE_COUNT > 0}
     <tr>
      <td class="sub_header">User</td>
      <td class="sub_header">IP Address</td>
     </tr>
     {LOOP REGISTERED_SESSIONS_ONLINE}
     <tr>
      <td class="standard_row_{REGISTERED_SESSIONS_ONLINE.row}">{REGISTERED_SESSIONS_ONLINE.user}</td>
      <td class="standard_row_{REGISTERED_SESSIONS_ONLINE.row}">{REGISTERED_SESSIONS_ONLINE.ip}</td>
     </tr>
     {!LOOP}
     <tr>
      <td class="standard_cell" colspan="2"></td>
     </tr>
     {!IF}
    </table>
    <br />

