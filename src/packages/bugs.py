"""This is probably overkill for packages.gentoo.org, but perhaps it can be
used elsewhere"""

__revision__ = '$Revision: 1.2 $'
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

        self.data = (self.bug_id, self.severity, self.priority,
            self.rep_platform, self.assigned_to, self.status, self.resolution,
            self.short_desc)
        
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
        return self.data

    def __iter__(self):
        """Same as above"""
        for field in self.data:
            yield field
            
    def __getitem__(self, index):
        """Makes me look like a tuple or list"""
        return self.data[index]
        
class BugFactory:
    """create bugs from dict data"""
    def __init__(self):
        """to shut pylint up"""
        pass
        
    def from_dict(self, mapping):
        """from_dict => BugFactory.from_dict(mapping).to_dict() == mapping"""
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
            
    def from_list_of_dicts(self, buglist):
        """when you have a list of dicts"""
        return [self.from_dict(mapping) for mapping in buglist]

    def from_list_of_lists(self, lists):
        """Return list of bugs from list of lists.  Lists must be in same
        order as call to Bug.__init__()
        """
        return [Bug(*bug_list) for bug_list in lists]

    from_db_query = from_list_of_lists

    def from_csv(self, csv_file):
        """fp should be a file object with CSV data in the format as returned
        by bugzlla"""
        
        import csv
        reader = csv.reader(csv_file)
        return [Bug(*data[:8]) for data in reader]

class HTMLWriter:
    """convert list of bugs to HTML"""
    def __init__(self, bugs, bugzilla_site=None):
        """where <bugs> is a list of Bugs"""

        table_begin = '<table class="buglist">'
        table_heading = ('<tr class="heading">'
            '<th class="bug_id">Bug ID</th>'
            '<th class="severity">Severity</th>'
            '<th class="priority">Priority</th>'
            '<th class="platform">Platform</th>'
            #'<th class="assigned_to">Assigned To</th>'
            '<th class="status">Status</th>'
            #'<th class="resolution">Resolution</th>'
            '<th class="description">Description</th>'
            '</tr>')
        rows = []
        for bug in bugs:
            bug_dict = bug.to_dict()
            if bugzilla_site:
                bug_id = ('<td class="bug_id">'
                    '<a href="http://%s/show_bug.cgi?id=%s">'
                    '%s</td>' % (bugzilla_site, bug_dict['bug_id'],
                    bug_dict['bug_id']))
            else:
                bug_id = '<td class="bug_id">%(bug_id)s</td>' % bug_dict
            
            bug_data = ('<td class="severity">%(severity)s</td>'
                '<td class="priority">%(priority)s</td>'
                '<td class="platform">%(rep_platform)s'
                #'<td class="assigned_to">%(assigned_to)s</td>'
                '<td class="status">%(status)s</td>'
                #'<td class="resolution">%(resolution)s</td>'
                '<td class="description">%(short_desc)s</td>'
                % bug_dict)
            row = '<tr class="bug">%(bug_id)s%(bug_data)s</tr>' % locals()
            rows.append(row) 
        table_end = '</table>'
        self.html = '\n    '.join([table_begin, table_heading] + rows + 
            [table_end])
    
    def __str__(self):
        return self.html
