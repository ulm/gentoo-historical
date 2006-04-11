<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:func="http://exslt.org/functions"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="func exslt">

<xsl:output encoding="UTF-8" method="xml" indent="yes" doctype-system="/dtd/guide.dtd"/>
<xsl:include href="/xsl/inserts.xsl" />

<xsl:variable name="devaway" select="document('/dyn/devaway/devaway.xml')"/>
<xsl:param name="select"/>

<xsl:template match="today">
  <!--<date><xsl:value-of select="exslt:node-set($devaway)/devaway/@date"/></date>-->
  <date><xsl:value-of select="func:today()"/></date>
</xsl:template>

<xsl:template match="/devaway">
  <mainpage id="projects" link="{@link}">
    <xsl:apply-templates/>
  </mainpage>
</xsl:template>

<xsl:template match="devs">
<chapter>
<title>Состояние</title>
<section>
<title>
Последнее обновление: <xsl:value-of select="exslt:node-set($devaway)/devaway/@date"/>
</title>
<body>
<table>
<tr>
 <th>Разработчик</th>
 <th>Состояние</th>
</tr>
<xsl:for-each select='exslt:node-set($devaway)/devaway/dev'>
  <xsl:sort select="@nick"/>
  <tr id="{@nick}">
  <th><xsl:value-of select="@nick"/></th>
  <ti>
   <xsl:choose>
    <xsl:when test="$select = @nick">
     <brite><xsl:value-of select="reason"/></brite>
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="reason"/>
    </xsl:otherwise>
   </xsl:choose>
  </ti>
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
