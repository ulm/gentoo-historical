"""marduk's helpin' heap 'o string functions"""


def replace_sub(s,new,start,end=None):
	if end is None:
		end = start
	s2 = s[:start] + new + s[end + 1:]
	newpos = start +  len(new)
	
	return (s2,newpos)
