"""This is probably overkill for packages.gentoo.org, but perhaps it can be
used elsewhere"""

__version__ = '$Revision: 1.1 $'
# $Source: /var/cvsroot/gentoo/src/packages/bugs.py,v $

# importers may want to override this.  This is the current(?)
# bugs.gentoo.org settings
STATUS = {'UNCONFIRMED': 'UNCONFIRMED',
    'NEW': 'NEW',
    'ASSIGNED': 'ASSIGNED',
    'REOPENED': 'REOPENED',
    'RESOLVED': 'RESOLVED',
    'VERIFIED': 'VERIFIED',
    'CLOSED': 'CLOSED'}
    
def parse_csv(line):
    """parse a line of CSV"""
    data = []
    indata = 0
    inquote = 0
    line = line.strip()
    cdata = ''
    prev_char = ''
    for char in line:
        if char == ',':
            if indata:
                if not inquote:
                    data.append(cdata)
                    cdata = ''
                    indata = 0
                else:
                    cdata = cdata + char
            elif prev_char == '' or prev_char == ',':
                data.append('')
        elif char == '"':
            if indata:
                data.append(cdata)
                indata = 0
                cdata = ''
                inquote = 0
            else:
                indata = 1
                inquote = 1
        elif indata:
            cdata = cdata + char
        else:
            indata = 1
            cdata = cdata = char
        prev_char = char
    if prev_char != '"':
        data.append(cdata)
    return data
    
class Bug:
    """a bugzilla bug"""
    def __init__(self, bug_id, severity, priority, rep_platform, assigned_to,
        status, resolution, short_desc):
        self.bug_id = bug_id
        self.severity = severity
        self.priority = priority
        self.rep_platform = rep_platform
        self.assigned_to = assigned_to
        self.status = status
        self.resolution = resolution
        self.short_desc = short_desc
        
    def to_dict(self):
        """convert to dict"""
        return {'bug_id': self.bug_id,
            'severity': self.severity,
            'priority': self.priority,
            'rep_platform': self.rep_platform,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'resolution': self.resolution,
            'short_desc': self.short_desc}
            
    def to_tuple(self):
        """convert to tuple"""
        return [self.bug_id, self.severity, self.priority, self.rep_platform, 
            self.assigned_to, self.status, self.resolution, self.short_desc]
        
class BugFactory:
    """create bugs from dict data"""
    def __init__(self):
        """to shut pylint up"""
        pass
        
    def fromDict(self, mapping):
        """from dict => BugFactory.fromDict(mapping).to_dict() == mapping"""
        bug_id = mapping.get("bug_id", "unknown")
        severity = mapping.get("severity")
        priority = mapping.get("priority")
        rep_platform = mapping.get("rep_platform")
        assigned_to = mapping.get("assigned_to")
        status = mapping.get("status")
        resolution = mapping.get("resolution")
        short_desc = mapping.get("short_desc")
        
        return Bug(bug_id, severity, priority, rep_platform, assigned_to, 
            status, resolution, short_desc)
            
    def fromListOfDicts(self, buglist):
        """when you have a list of dicts"""
        all = []
        for mapping in buglist:
            all.append(self.fromDict(mapping))
        return all
        
    def fromCSV(self, csv_file):
        """fp should be a file object with CSV data in the format as returned
        by bugzlla"""
        
        all = []
        for line in csv_file.readlines()[1:]:
            mapping = {}
            fields = parse_csv(line) 
            if len(fields) < 7:
                continue # wtf?
            #print fields
            (mapping['bug_id'], mapping['severity'], mapping['priority'], 
                mapping['rep_platform'], mapping['assigned_to'],
                mapping['status'], mapping['resolution'], 
                mapping['short_desc']) = fields[:8]
            all.append(self.fromDict(mapping))
        
        return all


class HTMLWriter:
    """convert list of bugs to HTML"""
    def __init__(self, bugs, bugzilla_site=None):
        """where <bugs> is a list of Bugs"""
        html = '<table class="buglist">\n'
        html = ('%s<tr class="heading"><th class="bug_id">Bug ID</th>'
            '<th class="severity">Severity</th><th class="priority">'
            'Priority</th><th class="platform">Platform</th>'
            #'<th class="assigned_to">Assigned To</th>'
            '<th class="status">Status</th>'
            #'<th class="resolution">Resolution</th>'
            '<th class="description">Description</th>'
            '</tr>\n' % html)
        for bug in bugs:
            bug_dict = bug.to_dict()
            html = html + '<tr class="bug">'
            if bugzilla_site:
                html = html + ('<td class="bug_id">'
                    '<a href="http://%s/show_bug.cgi?id=%s">'
                    '%s</td>' % (bugzilla_site, bug_dict['bug_id'],
                    bug_dict['bug_id']))
            else:
                html = html + '<td class="bug_id">%(bug_id)s</td>' % bug_dict
            
            html = html + ('<td class="severity">%(severity)s</td>'
                '<td class="priority">%(priority)s</td>'
                '<td class="platform">%(rep_platform)s'
                #'<td class="assigned_to">%(assigned_to)s</td>'
                '<td class="status">%(status)s</td>'
                #'<td class="resolution">%(resolution)s</td>'
                '<td class="description">%(short_desc)s</td>'
                '</tr>\n' % bug_dict)
        html = html + '</table>\n'
        self.html = html
    
    def __str__(self):
        return self.html
