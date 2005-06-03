<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:func="http://exslt.org/functions"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="func exslt">

<xsl:output encoding="UTF-8" method="xml" indent="yes" doctype-system="/dtd/guide.dtd"/>
<xsl:include href="/xsl/inserts.xsl" />

<xsl:variable name="devaway" select="document('http://dev.gentoo.org/~neysx/devaway/')"/>

<xsl:template match="today">
  <!--<date><xsl:value-of select="exslt:node-set($devaway)/devaway/@date"/></date>-->
  <date><xsl:value-of select="func:today()"/></date>
</xsl:template>

<xsl:template match="/devaway">
  <mainpage id="about" link="{@link}">
    <xsl:apply-templates/>
  </mainpage>
</xsl:template>

<xsl:template match="devs">
<chapter>
<title>Status</title>
<section>
<title>
Last update: <xsl:value-of select="exslt:node-set($devaway)/devaway/@date"/>
</title>
<body>
<table>
<tr>
 <th>Dev</th>
 <th>Status</th>
</tr>
<xsl:for-each select='exslt:node-set($devaway)/devaway/dev'>
  <xsl:sort select="@nick"/>
  <tr>
  <th><xsl:value-of select="@nick"/></th>
  <ti><xsl:value-of select="reason"/></ti>
  </tr>
</xsl:for-each>
</table>
</body>
</section>
</chapter>
</xsl:template>

<xsl:template match="*|@*|comment()|text()">
  <xsl:copy>
    <xsl:apply-templates select="*|@*|comment()|text()"/>
  </xsl:copy>
</xsl:template>
</xsl:stylesheet>
