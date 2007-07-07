<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output encoding="UTF-8" method="xml" indent="yes" doctype-system="/dtd/guide.dtd"/>
<xsl:include href="util.xsl"/>

<xsl:template match="/election">
<mainpage>
  <title><xsl:value-of select="title"/></title>

  <xsl:choose>
    <xsl:when test="author">
      <xsl:apply-templates select="author"/>
    </xsl:when>
    <xsl:otherwise>
      <author title="script generated">Gentoo Project</author>
    </xsl:otherwise>
  </xsl:choose>

  <xsl:if test="abstract">
    <abstract><xsl:value-of select="abstract"/></abstract>
  </xsl:if>

  <xsl:if test="version">
    <version><xsl:value-of select="version"/></version>
  </xsl:if>

  <date><xsl:value-of select="date"/></date>

  <chapter>
    <title><xsl:apply-templates select="title"/></title>
    <section>
    <title>Nominations status</title>
    <body>

    <note>
    Nominations are allowed from July 1st 0000 UTC to July 31st 2359 UTC via
    gentoo-dev mailling list.
    </note>
    <table>
      <tr><th>Accepted</th><th>Developer</th><th>Nickname</th><th>Devrel</th><th>Council</th><th>Trustee</th></tr>
      <xsl:apply-templates select="nominee"/>
    </table>
    </body>
    </section>
  </chapter>
</mainpage>
</xsl:template>

<!-- Nominee row -->
<xsl:template match="nominee">
  <tr>
    <ti>
      <xsl:apply-templates select="@accepted"/>
    </ti>
    <ti>
      <xsl:call-template name="fullname">
        <xsl:with-param name="nick" select="."></xsl:with-param>
      </xsl:call-template>
    </ti>
    <ti>
      <xsl:value-of select='translate(.,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")'/>
    </ti>
    <ti>
      <xsl:apply-templates select="@devrel"/>
    </ti>
    <ti>
      <xsl:apply-templates select="@council"/>
    </ti>
    <ti>
      <xsl:apply-templates select="@trustee"/>
    </ti>
  </tr>
</xsl:template>

<!-- Identity transform -->
<xsl:template match="author|mail//@*|mail//node()|author//node()|author//@*">
  <xsl:copy>
    <xsl:apply-templates select="node()|@*"/>
  </xsl:copy>
</xsl:template>

<!-- Capitalize -->
 <!-- List attributes explicitely in match="" if you add non yes/no attributes-->
<xsl:template match="nominee/@*"> 
  <xsl:value-of select='concat(translate(substring(.,1,1),"abcdefghijklmnopqrstuvwxyz","ABCDEFGHIJKLMNOPQRSTUVWXYZ"),translate(substring(.,2),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"))'/>
</xsl:template>

</xsl:stylesheet>
