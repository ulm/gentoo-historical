      

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
      
      {IF TOTAL_SCRIPTS > 0}
      <!-- Listing of all users in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="9" class="header">User Listing</td>
        </tr>

        <tr>
          <td class="sub_header">Name</td>
          <td class="sub_header">Version</td>
          <td class="sub_header">Submitter</td>
          <td class="sub_header">Category</td>
	  <td class="sub_header">Rank</td>
          <td class="sub_header">Language</td>
          <td class="sub_header">Date</td>
          <td class="sub_header">Approved By</td>
          <td class="sub_header">Status</td>
        </tr>
        {LOOP SCRIPT_LOOP}
	<tr>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.name}</a></td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.version}</td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.submitter}</td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.category}</td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.rank}</td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.language}</td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.date}</td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.approvedby}</td>
          <td class="standard_row_{SCRIPT_LOOP.row}">{SCRIPT_LOOP.status}</td>

	</tr>
        {!LOOP}
      </table>
      {!IF}

