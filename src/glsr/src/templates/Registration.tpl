
        <form name="registration" method="POST" action="index.py">
        <input type="hidden" name="page" value="create_user" />

        <!-- Registration Information -->
        <table width="90%" class="standard_table">
        <tr>
          <td colspan="2" class="header">Registration Information</td>
          </td>
        </tr>

        <tr>
          <td class="sub_header" colspan="2">
            Items marked with a * are required unless stated otherwise.
          </td>
        </tr>

        <!-- Username -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Username: *</td>
          <td class="standard_row_even" width="90%">
            <input type="text" class="text" name="alias" />
          </td>
        </tr>
        
        <!-- Email -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Email: *</td>
          <td class="standard_row_even">
            <input type="email" class="text" name="email" />
          </td>
        </tr>

        <!-- Password -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Password: *</td>
          <td class="standard_row_even">
            <input type="password" class="text" name="password1" />
          </td>
        </tr>

        <!-- Confirm Password -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Confirm Password: *</td>
          <td class="standard_row_even">
            <input type="password" class="text" name="password2" />
          </td>
        </tr>

        <tr>
          <td colspan="2" class="header">Profile Information</td>
          </td>
        </tr>

        <!-- Full name -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Full Name:</td>
          <td class="standard_row_even">
            <input type="text" class="text" name="fullname" />
          </td>
        </tr>
        
        <!-- Location -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Location:</td>
          <td class="standard_row_even">
            <input type="text" class="text" name="location" />
          </td>
        </tr>
        
        <!-- Language -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Favorite Programming Language:</td>
          <td class="standard_row_even">
            <input type="text" class="text" name="language" />
          </td>
        </tr>

        <!-- Website -->
	<tr>
          <td class="standard_row_even" nowrap="nowrap">Website:</td>
          <td class="standard_row_even">
            <input type="text" class="text" name="website" />
          </td>
        </tr>

        <tr>
          <td class="standard_row_odd" colspan="2" align="center">
            <input type="submit" class="button" value="Submit" />
            <input type="reset" class="button" value="Reset" />
          </td>
        </tr>
        
        </table>
        