<?xml version="1.0" encoding="UTF-8"?>
<!-- $Header: /var/cvsroot/gentoo/xml/htdocs/xsl/repositories.xsl,v 1.2 2010/05/03 23:05:46 robbat2 Exp $ -->
<!-- Used by [gentoo]/xml/htdocs/proj/en/overlays/repositories.xml -->
<!--
The source copy and history of this file is available from
http://git.overlays.gentoo.org/gitweb/?p=proj/repositories-xml-format.git
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                xmlns:str="http://exslt.org/strings"
                extension-element-prefixes="str exslt">

<xsl:output     encoding="UTF-8"
                omit-xml-declaration="no"
                doctype-system="/dtd/repositories.dtd"
                cdata-section-elements="description longdescription name"
                indent="yes"
                media-type="application/xml"/>

<xsl:strip-space elements="*"/>

<!-- Identity transform, just copy everything -->
<xsl:template match="/repositories | /repositories//*">
  <xsl:copy>
     <xsl:copy-of select="attribute::*" />
     <xsl:apply-templates select="node()" />
  </xsl:copy>
</xsl:template>
</xsl:stylesheet>
