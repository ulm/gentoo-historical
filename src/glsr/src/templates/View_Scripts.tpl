      <form name="view_scripts_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="scriptview">

      <!-- Listing of all users in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="4" class="header">Script Listing</td>
          <td colspan="4" class="header" style="text-align: right;">
          Order By:
          <select name="orderby">
            <option value="1">Author</option>
            <option value="2">Category</option>
            <option value="3">Language</option>
          </td>
        </tr>

        {IF MAIN_LOOP_LEN == 0}
        <tr>
          <td class="standard_cell" colspan="8">No Scripts Found</td>
        </tr>

        {ELSE}
        <tr>
          <td class="sub_header">Author</td>
	  <td class="sub_header">Name</td>
          <td class="sub_header">Category</td>
          <td class="sub_header">Language</td>
	  <td class="sub_header">Rank</td>
          <td class="sub_header">Version</td>
          <td class="sub_header">Date Created</td>
          <td class="sub_header">Approved By</td>
        </tr>
        
        {LOOP MAIN_LOOP}
	<!-- 0123456789012345678901234567890123456789 -->
	<tr>
          <td class="standard_row_{MAIN_LOOP.row}"><a href="index.py?page=profile&mode=viewprofile&uid={MAIN_LOOP.script_submitter_id}">{MAIN_LOOP.script_submitter}</a></td>
          <td class="standard_row_{MAIN_LOOP.row}"><a href="index.py?page=view_script&script_id={MAIN_LOOP.script_id}">{MAIN_LOOP.script_name}</a></td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_category}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_language}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_rank}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_version}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_date}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.subscript_approvedby}</td>
	</tr>
        {!LOOP}
        {!IF}
      </table>
