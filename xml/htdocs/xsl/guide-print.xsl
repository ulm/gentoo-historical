<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output encoding="utf-8" method="html" indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"/>

<xsl:include href="guide.xsl" />

<!-- Printable style for /guide -->
<xsl:template name="printdoclayout">
<html>
<head>
  <link title="new" rel="stylesheet" href="/css/main.css" type="text/css"/>
  <title>
    Printable Linux 
    <xsl:choose>
      <xsl:when test="/guide/@type='project'">Projects</xsl:when>
      <xsl:otherwise>Documentation</xsl:otherwise>
    </xsl:choose>
    -- 
    <xsl:choose>
      <xsl:when test="subtitle"><xsl:value-of select="title"/>: <xsl:value-of select="subtitle"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="title"/></xsl:otherwise>
    </xsl:choose>
  </title>
</head>
<body style="margin-right: 35mm;" bgcolor="#ffffff">

<!-- Content goes here -->
<xsl:call-template name="content" />

</body>
</html>
</xsl:template>

<xsl:template match="/guide">
  <xsl:call-template name="printdoclayout" />
</xsl:template>

</xsl:stylesheet>
