<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                xmlns:func="http://exslt.org/functions" 
                xmlns:date="http://exslt.org/dates-and-times"
                xmlns:str="http://exslt.org/strings"
		xmlns:dyn="http://exslt.org/dynamic"
		xmlns:xl="http://www.w3.org/1999/xlink"
		xmlns="http://docbook.org/ns/docbook"
                extension-element-prefixes="exslt func date dyn str">

<!--
  This stylesheet supports (or attempts to support) changing GuideXML (and
  handbook) to DocBook v5.

  Usage can be as simple as:
    $ xsltproc docbook.xsl /path/to/guide.xml > guide.docbook
-->

<xsl:output encoding="UTF-8" method="xml" indent="yes" />

<!-- Not using webroot paths as the stylesheet is currently intended for local
     use
-->
<xsl:include href="inserts.xsl" />

<xsl:template match="guide">
<article>
  <info>
    <title><xsl:value-of select="title" /></title>
  </info>

<xsl:for-each select="chapter">
  <xsl:call-template name="gchapter"/>
</xsl:for-each>

</article>
</xsl:template>

<xsl:template name="gchapter">
<section>
  <title><xsl:value-of select="title" /></title>
  <xsl:for-each select="section">
    <xsl:call-template name="gsection" />
  </xsl:for-each>
</section>
</xsl:template>

<xsl:template name="gsection">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
<section>
  <xsl:if test="@id">
    <xsl:attribute name="xml:id"><xsl:value-of select="@id" /></xsl:attribute>
  </xsl:if>
  <title><xsl:value-of select="title" /></title>
<xsl:apply-templates select="body"/>

</section>
</xsl:if>
</xsl:template>

<xsl:template match="book">
<book>
  <xsl:attribute name="version">5.0</xsl:attribute>
  <title><xsl:value-of select="title" /></title>
  <preface>
  <title>Abstract</title>
  <para>
    <xsl:value-of select="abstract" />
  </para>
  <para>
    Special thanks go to the following people, in no particular order, for
    their contributions, editing and authoring of the various Gentoo
    Handbooks:
  </para>
  <para>
    <xsl:for-each select="author">
      <xsl:value-of select="." /> (<xsl:value-of select="@title" />)
      <xsl:if test="position() != last()">, </xsl:if>
    </xsl:for-each>
  </para>
  </preface>

<xsl:apply-templates select="part" />

</book>
</xsl:template>

<xsl:template match="part">
<part>
<title><xsl:value-of select="title" /></title>

<xsl:apply-templates select="chapter" />

</part>
</xsl:template>

<xsl:template match="chapter">
<chapter>
<title><xsl:value-of select="title" /></title>

<xsl:apply-templates select="include" />

</chapter>
</xsl:template>

<xsl:template match="include">
<xsl:variable name="link" select="@href" />

<xsl:choose>
  <xsl:when test="document($link)/sections">
    <xsl:for-each select="document($link)/sections/section">
      <xsl:call-template name="c_section" />
    </xsl:for-each>
  </xsl:when>
  <xsl:when test="document($link)/included/body">
    <xsl:for-each select="document($link)/included/body">
      <xsl:apply-templates />
    </xsl:for-each>
  </xsl:when>
  <xsl:when test="document($link)/included/section">
    <xsl:for-each select="document($link)/included/section">
      <xsl:call-template name="c_section" />
    </xsl:for-each>
  </xsl:when>
  <xsl:otherwise>
    TODO-2
  </xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template name="c_section">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
<section>
  <xsl:if test="@id">
    <xsl:attribute name="xml:id"><xsl:value-of select="@id" /></xsl:attribute>
  </xsl:if>
  <title><xsl:value-of select="title" /></title>
  <xsl:apply-templates select="subsection|body" />
</section>
</xsl:if>
</xsl:template>

<xsl:template match="subsection">
<xsl:choose>
  <xsl:when test="title">
    <section>
      <title><xsl:value-of select="title" /></title>
      <xsl:apply-templates select="body" />
    </section>
  </xsl:when>
  <xsl:when test="include">
    <xsl:apply-templates />
  </xsl:when>
  <xsl:when test="body">
    <xsl:apply-templates />
  </xsl:when>
  <xsl:otherwise>
    TODO-1
  </xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template match="body">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
  <xsl:apply-templates />
</xsl:if>
</xsl:template>

<xsl:template match="p">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
  <para><xsl:apply-templates /></para>
</xsl:if>

</xsl:template>

<xsl:template match="pre">
<example>
  <title><xsl:value-of select="@caption" /></title>
  <programlisting>
<xsl:apply-templates />
  </programlisting>
</example>
</xsl:template>

<xsl:template match="ul">
<itemizedlist>
  <xsl:apply-templates />
</itemizedlist>
</xsl:template>

<xsl:template match="ol">
<orderedlist>
  <xsl:apply-templates />
</orderedlist>
</xsl:template>

<xsl:template match="li">
  <listitem>
    <para>
<xsl:apply-templates />
    </para>
  </listitem>
</xsl:template>

<xsl:template match="dl">
<itemizedlist>
  <xsl:apply-templates />
</itemizedlist>
</xsl:template>

<xsl:template match="dt">
<xsl:text disable-output-escaping="yes">&lt;listitem&gt;&lt;para&gt;</xsl:text>
<emphasis><xsl:apply-templates /></emphasis> - 
</xsl:template>

<xsl:template match="dd">
<xsl:apply-templates />
<xsl:text disable-output-escaping="yes">&lt;/para&gt;&lt;/listitem&gt;</xsl:text>
</xsl:template>

<xsl:template match="uri">
<link xl:href="{@link}"><xsl:apply-templates /></link>
</xsl:template>

<xsl:template match="c|i">
<command><xsl:apply-templates /></command>
</xsl:template>

<xsl:template match="e">
<emphasis><xsl:apply-templates /></emphasis>
</xsl:template>

<xsl:template match="path">
<filename><xsl:apply-templates /></filename>
</xsl:template>

<xsl:template match="table">
<xsl:variable name="numcol" select="count(tr[3]/*)"/>
<informaltable>
  <tbody>
  <xsl:apply-templates select="thead|tr"/>
  </tbody>
</informaltable>
</xsl:template>

<xsl:template match="thead">
<xsl:apply-templates />
</xsl:template>

<xsl:template match="tr">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
  <tr><xsl:apply-templates /></tr>
</xsl:if>
</xsl:template>

<xsl:template match="th">
<th><xsl:apply-templates /></th>
</xsl:template>

<xsl:template match="ti">
<xsl:choose>
  <xsl:when test="@colspan">
    <td colspan="{@colspan}"><xsl:apply-templates /></td>
  </xsl:when>
  <xsl:otherwise>
    <td><xsl:apply-templates /></td>
  </xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template match="note">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
  <note><para><xsl:apply-templates /></para></note>
</xsl:if>
</xsl:template>

<xsl:template match="impo">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
  <important><para><xsl:apply-templates /></para></important>
</xsl:if>
</xsl:template>

<xsl:template match="warn">
<xsl:if test="not(@test) or dyn:evaluate(@test)">
  <warning><para><xsl:apply-templates /></para></warning>
</xsl:if>
</xsl:template>

<xsl:template match="brite">
<emphasis><xsl:apply-templates /></emphasis>
</xsl:template>

</xsl:stylesheet>
