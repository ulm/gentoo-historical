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
         <td class="standard_cell" colspan="3" align="right"><input type="submit" class="button" name="flush" value="Flush Log" />&nbsp;&nbsp;</td>
      </tr>
    </table>
    <br />
    {!IF}

    <table width="90%" border="0" cellspacing="0" cellpadding="0" class="section_table">
      <tr>
        <td height="50" background="{GLSR_URL}images/header-bk.png">&nbsp;&nbsp;<span class="section_header_text">Who Is Online</span></td>
	<td width="50" height="50" align="center" valign="middle" background="{GLSR_URL}images/header-bk.png"><img src="{GLSR_URL}images/people.png" width="48" height="48"></td>
      </tr>
      <tr>
        <td height="30" colspan="2" class="stats_row_4"><span>&nbsp;&nbsp;{USER_ONLINE_LIST}</span></td>
      </tr>
    </table>

