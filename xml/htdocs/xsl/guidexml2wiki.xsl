<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                xmlns:func="http://exslt.org/functions"
                xmlns:dyn="http://exslt.org/dynamic"
                xmlns:str="http://exslt.org/strings"

                xmlns:feed="http://www.w3.org/2005/Atom"

                xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
                exclude-result-prefixes="opensearch feed"

                extension-element-prefixes="exslt func dyn str" >

<xsl:output encoding="UTF-8" method="text" indent="no" />
<xsl:preserve-space elements="pre" />
<!-- <xsl:preserve-space elements="li p pre" /> -->

<xsl:template match="guide"><xsl:value-of select="normalize-space(abstract)" />
<xsl:apply-templates />
<xsl:if test="//guide/author[not(@title='script generated')]">
== Acknowledgements ==

We would like to thank the following authors and editors for their contributions to this guide:
<xsl:for-each select="//guide/author">
* <xsl:choose><xsl:when test="mail/text()"><xsl:value-of select="mail" /></xsl:when><xsl:when test="mail"><xsl:value-of select="mail/@link" /></xsl:when><xsl:otherwise><xsl:value-of select="normalize-space()" /></xsl:otherwise></xsl:choose>
</xsl:for-each>
</xsl:if>

[[Category:Server and Security]]
</xsl:template>

<xsl:template match="author" />

<xsl:template match="abstract" />

<xsl:template match="chapter">
<!-- Ignore developers and subprojects as these will be provided by the wiki itself. -->
<xsl:if test="not(title='Developers') and not(title='Subprojects')">
== <xsl:value-of select="title" /> ==<xsl:text>

</xsl:text>
<xsl:apply-templates />
</xsl:if>
</xsl:template>

<xsl:template match="section">
<xsl:if test="preceding-sibling::section"><xsl:text>
</xsl:text>
</xsl:if>
<xsl:if test="title">
=== <xsl:value-of select="title" /> ===<xsl:text>

</xsl:text>
</xsl:if>
<xsl:choose>
<xsl:when test="include">
<xsl:variable name="doc" select="include/@href" />
<xsl:for-each select="document($doc)/included/section">
<xsl:if test="title">
=== <xsl:value-of select="title" /> ===<xsl:text>

</xsl:text>
</xsl:if>
<xsl:apply-templates />
</xsl:for-each>
</xsl:when>
<xsl:otherwise>
<xsl:apply-templates />
</xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template match="body"><xsl:apply-templates /></xsl:template>

<!-- 
  i is for in-pre commands, we cannot support that easily as we have no
  knowledge of what needs to be RootCmd, UserCmd, what is output, etc.
-->
<xsl:template match="i"><xsl:apply-templates /></xsl:template>

<xsl:template match="mail"><xsl:if test="string-length(preceding-sibling::text()) &gt; 1"><xsl:text> </xsl:text></xsl:if><xsl:choose><xsl:when test="link">{{Mail|<xsl:value-of select="@link" />|<xsl:value-of select="normalize-space()" />}}</xsl:when><xsl:otherwise>{{Mail|<xsl:value-of select="normalize-space()" />}}</xsl:otherwise></xsl:choose></xsl:template>

<xsl:template match="p"><xsl:apply-templates /><xsl:text> 

</xsl:text>
</xsl:template>

<xsl:template match="br" />
<xsl:template match="license" />

<!-- 
     var is formatting in pre, difficult to handle this
-->
<xsl:template match="var"><xsl:apply-templates /></xsl:template>

<!--
     stmt is formatting in pre, difficult to handle this
-->
<xsl:template match="stmt"><xsl:apply-templates /></xsl:template>

<!--
     const is formatting in pre, difficult to handle this
-->
<xsl:template match="const"><xsl:apply-templates /></xsl:template>

<xsl:template match="uri"><xsl:if test="string-length(preceding-sibling::text()) &gt; 1"><xsl:text> </xsl:text></xsl:if><xsl:choose><xsl:when test="starts-with(@link, 'http')">[<xsl:value-of select="@link" /><xsl:text> </xsl:text><xsl:value-of select="normalize-space(text())" />]</xsl:when><xsl:when test="not(@link)">[<xsl:value-of select="normalize-space(text())" /><xsl:text> </xsl:text><xsl:value-of select="normalize-space(text())" />]</xsl:when><xsl:when test="not(starts-with(@link, '#'))">[http://www.gentoo.org/<xsl:value-of select="@link"/><xsl:text> </xsl:text><xsl:value-of select="normalize-space(text())" />]</xsl:when><xsl:when test="starts-with(@link, '#')">[[<xsl:value-of select="@link" />]]</xsl:when></xsl:choose><xsl:if test="string-length(following-sibling::text()) &gt; 1"><xsl:text> </xsl:text></xsl:if></xsl:template>

<xsl:template match="e"> ''<xsl:apply-templates />'' </xsl:template>

<xsl:template match="ul"><xsl:text>
</xsl:text><xsl:apply-templates /><xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="ol">
<xsl:apply-templates /></xsl:template>

<xsl:template match="li">
<xsl:choose><xsl:when test="name(..)='ul'"><xsl:for-each select="ancestor::ul|ancestor::ol">*</xsl:for-each><xsl:text> </xsl:text><xsl:apply-templates /></xsl:when><xsl:when test="name(..)='ol'"><xsl:for-each select="ancestor::ol|ancestor::ul">#</xsl:for-each><xsl:text> </xsl:text><xsl:apply-templates /></xsl:when><xsl:otherwise>OH NOES HERE IT GOES!</xsl:otherwise></xsl:choose><xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="sup">&lt;sup&gt;<xsl:apply-templates />&lt;/sup&gt;</xsl:template>

<xsl:template match="sub">&lt;sub&gt;<xsl:apply-templates />&lt;/sub&gt;</xsl:template>

<xsl:template match="title" />

<xsl:template match="date" />

<xsl:template match="version" />

<xsl:template match="c"><xsl:if test="string-length(preceding-sibling::text()) &gt; 1"><xsl:text> </xsl:text></xsl:if>&lt;code&gt;<xsl:apply-templates />&lt;/code&gt;<xsl:if test="string-length(following-sibling::text()) &gt; 1"><xsl:text> </xsl:text></xsl:if></xsl:template>

<xsl:template match="pre"><xsl:text>
</xsl:text>
{{CodeBox|title=<xsl:value-of select="@caption" />|&lt;pre&gt;<xsl:apply-templates />&lt;/pre&gt;
}}
<xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="comment"><xsl:apply-templates /></xsl:template>

<xsl:template match="path"> {{Path|<xsl:apply-templates />}} </xsl:template>

<xsl:template match="b"><xsl:if test="string-length(preceding-sibling::text()) &gt; 1"><xsl:text> </xsl:text></xsl:if>'''<xsl:apply-templates />'''<xsl:if test="string-length(following-sibling::text()) &gt; 1"><xsl:text> </xsl:text></xsl:if></xsl:template>

<xsl:template match="warn">
{{Warning|<xsl:apply-templates />}}
</xsl:template>

<xsl:template match="impo">
{{Important|<xsl:apply-templates />}}
</xsl:template>

<xsl:template match="brite">'''<xsl:apply-templates />'''</xsl:template>

<xsl:template match="note">
{{Note|<xsl:apply-templates />}}
</xsl:template>

<xsl:template match="table">

{| class="wikitable" style="text-align: left;" <xsl:apply-templates />
|-
|}

</xsl:template>

<xsl:template match="tr">
|- <xsl:apply-templates />
</xsl:template>

<xsl:template match="th">
! <xsl:apply-templates />
</xsl:template>
<xsl:template match="ti">
| <xsl:apply-templates />
</xsl:template>

<xsl:template match="dl">
{| class="wikitable" style="text-align: left;"
<xsl:apply-templates />
|-
|}
</xsl:template>

<xsl:template match="dt">
! <xsl:apply-templates />
</xsl:template>

<xsl:template match="dd">
| <xsl:apply-templates />
</xsl:template>

<xsl:template match="text()">
<xsl:choose>
<xsl:when test="ancestor::pre"><xsl:value-of select="." /></xsl:when>
<xsl:otherwise><xsl:value-of select="normalize-space()" /></xsl:otherwise>
</xsl:choose>
</xsl:template>

</xsl:stylesheet>
