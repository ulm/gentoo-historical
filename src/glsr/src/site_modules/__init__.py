__all__ = [
    "Page_Login",
    "Page_Main",
    "Page_Script",
    "Page_Search",
    "View_Script"
    ]

# The page to display when all else fails.
# Note that this display module should not have any required form inputs.
failover = "Page_Main"
 
class SiteModule:
    """The parent class for all site modules."""

    import Template as TemplateHandler

    tmpl = TemplateHandler.Template()
    pages = []
    show_border = True


class Redirect(Exception): pass
