
        <form name="memberlist" method="GET" action="index.py">
        <input type="hidden" name="page" value="memberlist" />

        <table width="90%" class="standard_table">
        <tr>
          <td colspan="4" class="header">Member List</td>
          <td colspan="4" class="header" style="text-align: right;">
            Order By:
            <select name="orderby">
              <option value="id">ID</option>
              <option value="alias">Username</option>
              <option value="email">Email</option>
              <option value="location">Location</option>
              <option value="joined">Joined</option>
              <option value="scripts">Scripts</option>
              <option value="rank">Rank</option>
              <option value="website">Website</option>
            </select>
          </td>
        </tr>

        <tr>
          <td class="sub_header">ID</td>
          <td class="sub_header">Username</td>
          <td class="sub_header">Email</td>
          <td class="sub_header">Location</td>
          <td class="sub_header">Joined</td>
          <td class="sub_header">Scripts</td>
          <td class="sub_header">Rank</td>
          <td class="sub_header">Website</td>
        </tr>

        {LOOP MEMBER_LOOP}
        <tr>
          <td class="standard_row_even">{MEMBER_LOOP.user_id}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_alias}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_email}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_location}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_joined}</td>
          <td class="standard_row_even">{MEMBER_LOOP.script_count}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_rank}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_website}</td>
        </tr>
        {!LOOP}
        
        </table>
