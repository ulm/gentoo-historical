__all__ = {
    "Page_Login": ["login", "perform_login", "logout"],
    "Page_Main": ["main"],
    "Page_Script": ["create_script", "save_script"],
    "Page_Search": ["script_search"],
    "View_Script": ["view_script", "post_comment"],
    "Memberlist": ["memberlist"],
    "Register": ["register", "create_user"]
    }

# The page to display when all else fails.
# Note that this display module should not have any required form inputs.
failover = {"module": "Page_Main", "page": "main"}
