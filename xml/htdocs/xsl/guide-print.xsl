<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output encoding="utf-8" method="html" indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"/>

<xsl:include href="guide.xsl" />

<!-- This file can be deleted once the AxKit config has been updated -->

<xsl:template match="/guide">
  <xsl:call-template name="doclayout" />
</xsl:template>

</xsl:stylesheet>
