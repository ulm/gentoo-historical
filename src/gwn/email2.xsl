<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="text" indent="no"/>

<xsl:template match="guide">---------------------------------------------------------------------------
<xsl:apply-templates select="title"/>
http://www.gentoo.org/news/en/gwn/current.xml
<xsl:apply-templates select="abstract"/> 
<xsl:text>
---------------------------------------------------------------------------</xsl:text>
<xsl:apply-templates select="chapter|ignoreinguide"/>
<xsl:text>
</xsl:text>
<xsl:for-each select="author">
<xsl:value-of select="mail"/><xsl:text> &lt;</xsl:text><xsl:value-of select="mail/@link"/>
<xsl:text>&gt; - </xsl:text><xsl:value-of select="@title"/>
<xsl:text>
</xsl:text>
</xsl:for-each>
</xsl:template>

<xsl:template match="chapter">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="chapter/title">
<xsl:text>
=
</xsl:text>
<xsl:number level="any" count="//chapter/title"/>. <xsl:value-of select="."/>
=
</xsl:template>


<xsl:template match="section">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="section/title">
  <xsl:text>
</xsl:text>
<xsl:apply-templates/>
-
</xsl:template>

<xsl:template match="body">
<xsl:apply-templates/>
</xsl:template>

<xsl:template match="p">
<xsl:text>
</xsl:text>
<xsl:apply-templates/>
<xsl:text>
</xsl:text>
  <xsl:for-each select=".//uri|.//mail">
  <xsl:variable name="Link"><xsl:choose><xsl:when test="starts-with(@link, '/')"><xsl:value-of select="concat('http://www.gentoo.org',@link)"/></xsl:when><xsl:otherwise><xsl:value-of select="@link"/></xsl:otherwise></xsl:choose></xsl:variable>
<xsl:text>
 </xsl:text><xsl:number level="any" count="p//uri|p//mail|ul//uri|ul//mail"/>. <xsl:value-of select="$Link"/>
  </xsl:for-each>
<xsl:if test=".//uri|.//mail">
<xsl:text>
</xsl:text>
</xsl:if>
</xsl:template>

<xsl:template match="table">
<xsl:text>
</xsl:text>
<xsl:apply-templates/>
<xsl:text>
</xsl:text>
  <xsl:for-each select=".//uri|.//mail">
  <xsl:variable name="Link"><xsl:choose><xsl:when test="starts-with(@link, '/')"><xsl:value-of select="concat('http://www.gentoo.org',@link)"/></xsl:when><xsl:otherwise><xsl:value-of select="@link"/></xsl:otherwise></xsl:choose></xsl:variable>
<xsl:text>
 </xsl:text><xsl:number level="any" count="p//uri|p//mail|ul//uri|ul//mail|table//uri|table//mail"/>. <xsl:value-of select="$Link"/>
  </xsl:for-each>
<xsl:if test=".//uri|.//mail">
<xsl:text>
</xsl:text>
</xsl:if>
</xsl:template>

<xsl:template match="ul">
  <xsl:apply-templates/>
  <xsl:for-each select=".//uri|.//mail">
  <xsl:variable name="Link"><xsl:choose><xsl:when test="starts-with(@link, '/')"><xsl:value-of select="concat('http://www.gentoo.org',@link)"/></xsl:when><xsl:otherwise><xsl:value-of select="@link"/></xsl:otherwise></xsl:choose></xsl:variable>
<xsl:text>
 </xsl:text><xsl:number level="any" count="p//uri|p//mail|ul//mail|ul//uri|table//uri|table//mail"/>. <xsl:value-of select="$Link"/>
  </xsl:for-each>
<xsl:if test=".//uri|.//mail">
<xsl:text>
</xsl:text>
</xsl:if><xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="li">
<xsl:text>
 * </xsl:text><xsl:apply-templates/>
</xsl:template>

<xsl:template match="note">
Note: <xsl:value-of select="."/>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="uri|mail">
<xsl:value-of select="."/><xsl:text></xsl:text>[<xsl:number level="any" count="p//uri|p//mail|ul//uri|ul//mail|table//uri|table//mail"/>
<xsl:text>]</xsl:text>
</xsl:template>

<xsl:template match="figure">
<xsl:variable name="Link"><xsl:choose><xsl:when test="starts-with(@link, '/')"><xsl:value-of select="concat('http://www.gentoo.org',@link)"/></xsl:when><xsl:otherwise><xsl:value-of select="@link"/></xsl:otherwise></xsl:choose></xsl:variable>
<xsl:text>
Figure </xsl:text><xsl:number count="//chapter"/><xsl:text>.</xsl:text><xsl:number level="single" count="figure"/>: <xsl:value-of select="@caption"/>
<xsl:text>
</xsl:text><xsl:value-of select="$Link"/>
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="pre">
<xsl:text>
---------------------------------------------------------------------------
| Code Listing </xsl:text><xsl:number count="//chapter"/><xsl:text>.</xsl:text><xsl:number level="single" count="pre"/>:
|<xsl:value-of select="normalize-space(@caption)"/>
<xsl:text>-------------------------------------------------------------------------
</xsl:text><xsl:value-of select="."/>
<xsl:text>
---------------------------------------------------------------------------
</xsl:text>
</xsl:template>

<xsl:template match="abstract">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="ignoreinemail">
</xsl:template>
<xsl:template match="ignoreinguide">
  <xsl:apply-templates/>
</xsl:template>

</xsl:stylesheet>


