#!/usr/bin/env python2

# Copyright 2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
#

"""The GLSR Setup Script.

Note that this script will need the root db username and password to create
the database and the database user. (This isn't actually implemented yet)

TODO:
  - Implement code that will create the database and db user permissions.
  - Don't try to create the database or tables if they already exist. Or at
    least drop them first.
"""

__revision__ = '$Id: setup.py,v 1.1 2005/03/27 04:02:34 hadfield Exp $'
__modulename__ = 'setup'

import os
import re
import sys
sys.path.insert(0, "../")

import config
from core.template import Template as template_handler
from core.db.mysql import MySQL as db_handler

###############################################################################
# Setup DB regular expressions
# These expressions are used for parsing the mysql.schema file. To add support
# for an additional database all you need to do is add three new regular
# expressions for that db.
# For example, to add support for postgres, you'll need the following regex's:
# _postgres_db_re, _postgres_table_re, and postgres_table_name_re.

# Create the database handler object.
_db_obj = db_handler(config.db)

# Database specific db matching regex's.
_mysql_db_re = r'(?is)CREATE\s+DATABASE\s+\w+\s*;'

# Database specific table matching regex's. Used for getting a table definition
# from the db schema. Note that %s represents the table name.
_mysql_table_re = r'((?is)CREATE\s+TABLE\s+%s\s*\([^;]*);'

# Database specific table name matching regex's. Used for getting a list of
# table names in the database schema.
_mysql_table_name_re = r'(?is)CREATE\s+TABLE\s+([^\s]+)'

# Set the table name and db matching regex to the appropriate database.
_db_re = eval("_%s_db_re" % config.db["db_type"])
_table_re = eval("_%s_table_re" % config.db["db_type"])
_table_name_re = eval("_%s_table_name_re" % config.db["db_type"])

def str_indent(str_in, indent_amt):
    
    indent_str = " " * indent_amt
    return indent_str + str_in.replace("\n", "\n" + indent_str)

def load_schema(schema_loc, values):

    schema_tmpl = template_handler()
    schema_tmpl.param("TBL_PREFIX", config.db["prefix"])
    schema_tmpl.param("DB_NAME", config.db["db"])
    schema_tmpl.param("LANGUAGE_LOOP", [], "loop")
    
    if values.has_key("USER_LOOP"):
        schema_tmpl.param("USER_LOOP", values["USER_LOOP"], "loop")
    else:
        schema_tmpl.param("USER_LOOP", [], "loop")
    
    schema_tmpl.compile(schema_loc, cache = False)
    return schema_tmpl.output()

def add_user(user_type = ""):

    from getpass import getpass

    if user_type != "":
        user_type += " "
    
    alias = raw_input("\n%suser alias: " % user_type)
    if len(alias) == 0:
        print "ERROR: Zero length username"
        sys.exit(1)

    passwd = getpass("Password: ")
    if len(passwd) == 0:
        print "ERROR: Zero length password"
        sys.exit(1)
    
    passwd2 = getpass("Re-type password: ")
    if passwd != passwd2:
        print "ERROR: passwords do not match"
        sys.exit(1)

    fullname = raw_input("Full Name: ")
    email = raw_input("Email: ")

    return {"alias": alias, "passwd": passwd, "fullname": fullname,
            "email": email}

###############################################################################
# The database building/creation methods

def _list_tables(schema):
    """Returns a list of table names in the specified schema."""

    return re.findall(_table_name_re, schema)

def create_database(schema):

    db_match = re.search(_db_re, schema)
        
    if db_match is None:
        raise SetupError("DB create not defined in schema" % table)

    print db_match.group(0)

    _db_obj.query(db_match.group(0), fetch="none")
    
    
def create_tables(tables, schema):
    """Create all tables in 'tables'. Each table must be defined in schema."""

    for table in tables:
        
        print "  >>> " + table
        table_match = re.search(_table_re % table, schema)
        
        if table_match is None:
            raise SetupError("Table '%s' not defined in schema" % table)

        #print str_indent(table_str.group(0), 4)
        #print ""
        
        _db_obj.query(table_match.group(1), fetch="none")

def insert_data(table, schema):

    start = schema.find("# begin %s-data-insert" % table)
    start = start + len("# begin %s-data-insert" % table)
    end = schema.find("# end %s-data-insert" % table)

    query_str = schema[start:end].strip()
    if -1 not in (start, end) and query_str != "":
        print "  >>> " + table
        _db_obj.query(schema[start:end].strip(), fetch = "none")

class SetupError(Exception): pass


if __name__ == '__main__':

    # Setup directories and files
    print "Creating script repository directories and files:"
    print "  Creating log folder (%s)" % config.logging_loc
    if not os.path.exists(config.logging_loc):
        os.makedirs(config.logging_loc)
    
    print "  Creating template cache folder (%s)" % config.template_cache
    if not os.path.exists(config.template_cache):
        os.makedirs(config.template_cache)

    user_loop = []
    admin_info = add_user("Admin")
    admin_info["rank"] = 0
    admin_info["type"] = 3
    user_loop.append(admin_info)

    # Load the schema file
    schema_loc = config.root + "/setup/schema/%s.schema" % config.db["db_type"]
    schema = load_schema(schema_loc, {"USER_LOOP": user_loop})

    # Create the database and tables
    #print "Creating GLSR %s database" % config.db["db_type"]
    #create_database(schema)

    print "\nCreating %s tables" % config.db["db_type"]
    create_tables(_list_tables(schema), schema)

    print "\nInserting default data:"
    insert_data("state", schema)

    print "\nInserting language data:"
    insert_data("language", schema)

    # Add the admin user
    print "\nCreating admin user %s..." % (admin_info["alias"])
    insert_data("user", schema)

    print

