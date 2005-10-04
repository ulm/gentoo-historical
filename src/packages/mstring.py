"""marduk's helpin' heap 'o string functions"""


def replace_sub(string, new, start, end=None):
    """Replacing substring of s with new, return new string, and position
    directly after substitution
    """
    if end is None:
        end = start
    string2 = string[:start] + new + string[end + 1:]
    newpos = start +  len(new)

    return (string2, newpos)
