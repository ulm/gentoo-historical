
      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}
      
      {IF WARN_MESSAGE == 1}
      <font class="warn_message">No Scripts Found With That ID!</font><br /><br />
      {!IF}


      {IF WARN_MESSAGE != 1}
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="2" class="header">View Script</td>
        </tr>

        <tr>
          <td class="skinny_cell" width="100">
            <font class="instructional">Name:</font>
          </td>
          <td class="skinny_cell">
            <font class="data">{NAME}</font>
          </td>
        </tr>

        <tr>
          <td class="skinny_cell" width="100">
            <font class="instructional">Author:</font>
          </td>
          <td class="skinny_cell">
            <font class="data">{AUTHOR}</font>
          </td>
        </tr>

        <tr>
          <td class="skinny_cell" width="100">
            <font class="instructional">Creation Date:</font>
          </td>
          <td class="skinny_cell">
            <font class="data">{CREATION_DATE}</font>
          </td>
        </tr>

        <tr>
          <td class="skinny_cell">
            <font class="instructional">Description:</font>
          </td>
          <td class="skinny_cell">
            <font class="data">{DESCR}</font>
          </td>
        </tr>
        
        <tr>
          <td class="skinny_cell">
            <font class="instructional">Version:</font>
          </td>
          <td class="skinny_cell">
            <font class="data">{VERSION}</font>
          </td>
        </tr>

        <tr>
          <td class="skinny_cell">
            <font class="instructional">Category:</font>
          </td>
          <td class="skinny_cell">
            <font class="data">{CATEGORY}</font>
          </td>
        </tr>
        
        <tr>
          <td class="skinny_cell">
            <font class="instructional">Language:</font>
          </td>
          <td class="skinny_cell">
            <font class="data">{LANGUAGE}</font>
          </td>
        </tr>

        <tr>
          <td class="skinny_cell" valign="top" colspan="2">
            <font class="instructional">Body:</font><br />
            <div class="codebox">
            <pre><font class="data">{BODY}</font></pre>
            </div>
          </td>
        </tr>

        <tr><td class="skinny_cell" colspan="2">&nbsp;</td></tr>
      </table>

      <br />

      <table width="90%" class="standard_table">
        <tr>
          <td colspan="2" class="header">Comments</td>
        </tr>

        <tr>
          <td class="sub_header" width="100">
            Author
          </td>
          <td class="sub_header">
            Message
          </td>
        </tr>

        {LOOP COMMENTS_LOOP}
        <tr>
          <td class="skinny_cell" colspan="2">
            <table cellspacing="0" cellpadding="0" border="0" width="100%">
              <tr>
                <td class="comment_post_header">
                  Poster: {COMMENTS_LOOP.submitter}
                  &nbsp;&nbsp;&nbsp;
                  Posted: {COMMENTS_LOOP.date}
                  &nbsp;&nbsp;&nbsp;
                  Post Subject: {COMMENTS_LOOP.comment_subject}
                </td>
              </tr>
              <tr>
                <td class="comment_block">
                  <font class="comment_text">{COMMENTS_LOOP.comment_body}</font>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        {!LOOP}

        {IF COMMENTS_LOOP_COUNT == 0}
        <tr>
          <td class="standard_cell" colspan="2">
            No Comments Posted For This Script
          </td>
        </tr>
        {!IF}

      </table>

      <br />

      <form name="view_script_form" method="GET" action="index.py">
      <input type="hidden" name="page" value="post_comment" />
      <input type="hidden" name="script_id" value="{SCRIPT_ID}" />
      <input type="hidden" name="subscript_id" value="{SUBSCRIPT_ID}" />
      
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="2" class="header">Post New Comment</td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">Subject:</font><br />
           <input type="text" class="text-long" name="subject" value="" />
          </td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">Body:</font><br />
           <textarea rows="10" style="width: 100%;" class="text" name="body"></textarea>
          </td>
        </tr>

        <tr>
          <td class="standard_cell">
            <input type="submit" class="button" name="post_comment" value="Post" />
          </td>
        </tr>

      </table>
      
      </form>      
      {!IF}

