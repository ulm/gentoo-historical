      <form name="user_control_form" method="POST" action="index.py">
      <input type="hidden" name="page" value="save_script">
      <input type="hidden" name="script_id" value="{SCRIPT_ID}" />
      <input type="hidden" name="parent_script_id" value="{PARENT_SCRIPT_ID}" />

      {IF MESSAGE != ""}
      <font class="message">{MESSAGE}</font><br /><br />
      {!IF}


      <!-- The form to add a new script -->
      <table width="90%" class="standard_table">
        <tr>
          <td colspan="" class="header">{IF SCRIPT_ID == 0}Add New Script{ELSE}Modify Script{!IF}</td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">Name:</font><br />
           <input type="text" class="text-long" name="name" value="{NAME}" />
          </td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">Description:</font><br />
           <input type="text" class="text-long" name="descr" value="{DESCR}" />
          </td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Version (numeric):</font><br />
           <input type="text" class="text" name="version" value="{VERSION}" />
          </td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">Categories:</font><br />
           {LOOP CATEGORY_LOOP}<!-- 012345678901234567 -->
           <input type="checkbox" name="category_ids" value="{CATEGORY_LOOP.category_id}" /> {CATEGORY_LOOP.category_name}
           <br />
           {!LOOP}
          </td>
        </tr>
        
	<tr>
          <td class="standard_cell">
           <font class="instructional">Language:</font><br />
           <select name="language_id">
             <option value="0">Select a Language</option>
             {LOOP LANGUAGE_LOOP}
             <!-- {LANGUAGE_LOOP.language_name} -->
             <option value="{LANGUAGE_LOOP.language_id}" {IF LANGUAGE_LOOP.language_id == LANGUAGE_ID}selected{!IF}>{LANGUAGE_LOOP.language_name}</option>
             {!LOOP}
           </select>
          </td>
        </tr>
        
        <tr>
          <td class="standard_cell">
           <font class="instructional">Body:</font><br />
           <textarea rows="15" style="width: 100%;" class="text" name="body">{BODY}</textarea>
          </td>
        </tr>

        <tr>
          <td class="standard_cell">
           <font class="instructional">ChangeLog:</font><br />
           <textarea rows="5" style="width: 100%;" class="text" name="changelog">{CHANGELOG}</textarea>
          </td>
        </tr>
        
        <tr>
           <td class="standard_cell">
           <input type="submit" class="button" name="save_script" value="Save" />
           &nbsp;&nbsp;
           <input type="submit" class="button" name="publish_script" value="Publish" />
           &nbsp;&nbsp;
           <input type="submit" class="button" name="get_script_reviewed" value="Submit for Review" />
           </td>
        </tr>
      </table>


      </form>
