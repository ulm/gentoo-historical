<html>
<head>
</head>
<body>
<a href="{LINK_URI}">{LINK_TEXT}</a>
<ul>
{LOOP MYLOOP}
<il> {MYLOOP}
{!LOOP}
</ul>
{IF RANK == "Admin"}
<font color="#000000">You're an Admin!</font>
{!IF}
</body>
</html>
