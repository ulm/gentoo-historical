      <form name="view_scripts_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="scriptview">

      <!-- Listing of all users in the system -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="8" class="header">Script Listing<br />
          Order By:
          <select name="orderby">
            <option value="1">Author</option>
            <option value="2">Category</option>
            <option value="3">Language</option>
          </td>
        </tr>

        <tr>
          <td class="sub_header">Author</td>
	  <td class="sub_header">Name</td>
          <td class="sub_header">Category</td>
          <td class="sub_header">Language</td>
	  <td class="sub_header">Rank</td>
          <td class="sub_header">Version</td>
          <td class="sub_header">Date Approved</td>
          <td class="sub_header">Approved By</td>
        </tr>
        {LOOP MAIN_LOOP}
	<tr>
          <td class="standard_row_{MAIN_LOOP.row}"><a href="index.py?page=profile&mode=viewprofile&uid={MAIN_LOOP.script_submitter_id}">{MAIN_LOOP.script_submitter}</a></td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_name}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_category}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_language}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_rank}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_version}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_approved}</td>
          <td class="standard_row_{MAIN_LOOP.row}">{MAIN_LOOP.script_approved_by}</td>
	</tr>
        {!LOOP}
      </table>
