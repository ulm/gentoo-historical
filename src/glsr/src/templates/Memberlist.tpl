
        <form name="memberlist" method="GET" action="index.py">
        <input type="hidden" name="page" value="memberlist" />

        <table width="90%" class="standard_table">
        <tr>
          <td colspan="4" class="header">Member List</td>
          <td colspan="5" class="header" style="text-align: right;">
            Sort By:
            <select name="sortby">
              <option value="user_id"
                {IF SORTBY == "user_id"}selected{!IF}>ID</option>
              <option value="user_alias"
                {IF SORTBY == "user_alias"}selected{!IF}>Username</option>
              <option value="user_email"
                {IF SORTBY == "user_email"}selected{!IF}>Email</option>
              <option value="user_location"
                {IF SORTBY == "user_location"}selected{!IF}>Location</option>
              <option value="user_joined"
                {IF SORTBY == "user_joined"}selected{!IF}>Joined</option>
              <option value="script_count"
                {IF SORTBY == "script_count"}selected{!IF}>Scripts</option>
              <option value="user_rank"
                {IF SORTBY == "user_rank"}selected{!IF}>Rank</option>
              <option value="user_language"
                {IF SORTBY == "user_language"}selected{!IF}>Language</option>
              <option value="user_website"
                {IF SORTBY == "user_website"}selected{!IF}>Website</option>
            </select>
            
            Order:
            <select name="order">
              <option value="a" {IF ORDER == "a"}selected{!IF}>
                      Ascending</option>
              <option value="d" {IF ORDER == "d"}selected{!IF}>
                      Descending</option>
            </select>
            <input type="submit" class="button" name="sort" value="Sort" />
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
          <td class="sub_header">Language</td>
          <td class="sub_header">Website</td>
        </tr>

        {LOOP MEMBER_LOOP}
        {IF MEMBER_LOOP._is_even == 1}
        <tr>
          <td class="standard_row_even">{MEMBER_LOOP.user_id}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_alias}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_email}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_location}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_joined}</td>
          <td class="standard_row_even">{MEMBER_LOOP.script_count}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_rank}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_language}</td>
          <td class="standard_row_even">{MEMBER_LOOP.user_website}</td>
        </tr>
        {ELSE}
        <tr>
          <td class="standard_row_odd">{MEMBER_LOOP.user_id}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.user_alias}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.user_email}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.user_location}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.user_joined}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.script_count}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.user_rank}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.user_language}</td>
          <td class="standard_row_odd">{MEMBER_LOOP.user_website}</td>
        </tr>
        {!IF}
        {!LOOP}

        </table>

        <table width="90%" border="0">
        <tr>
          <td align="right">
            <font class="instructional">Page
            
            {LOOP PAGE_LOOP}
              {IF CURRENT_PAGE == PAGE_LOOP.page}
              <font color="black">{PAGE_LOOP.page}</font>
              {ELSE}
              <a href="{GLSR_URL}?page=memberlist&sortby={SORTBY}&order={ORDER}&sort=Sort&start={PAGE_LOOP.start}">{PAGE_LOOP.page}</a>
              {!IF}
            {!LOOP}
            
            {IF PAGE_LOOP_LEN > 1}
            <a href="{GLSR_URL}?page=memberlist&sortby={SORTBY}&order={ORDER}&sort=Sort&start={NEXT_START}">Next</a>
            {!IF}
            
            </font>
          </td>
        </tr>
        </table>
