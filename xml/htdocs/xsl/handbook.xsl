<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!-- Define global variables; if a user has
     already defined those, this is a NOP -->
<xsl:param name="part">0</xsl:param>
<xsl:param name="chap">0</xsl:param>

<!-- A book -->
<xsl:template match="/book">
  <!-- If chap = 0, show an index -->
  <xsl:choose>
    <xsl:when test="$part != 0">
      <xsl:apply-templates select="part" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$style = 'printable'">
          <xsl:call-template name="printdoclayout" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="doclayout"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- Content of /book -->
<xsl:template name="bookcontent">
  <xsl:call-template name="menubar" />
  <h1><xsl:value-of select="title" /></h1>
  <xsl:if test="$style = 'printable'">
    <xsl:apply-templates select="author" />
  </xsl:if>
  <p>Content:</p>
  <ul>
    <xsl:for-each select="part">
      <xsl:param name="curpart" select="position()" />
      <li>
        <b><a href="?part={$curpart}&amp;chap=0&amp;style={$style}"><xsl:value-of select="title" /></a></b>
        <xsl:if test="abstract">
          <br />
          <xsl:value-of select="abstract" />
        </xsl:if>
        <ol>
          <xsl:for-each select="chapter">
            <xsl:param name="curchap" select="position()" />
            <li>
              <b><a href="?part={$curpart}&amp;chap={$curchap}&amp;style={$style}"><xsl:value-of select="title" /></a></b>
              <xsl:if test="abstract">
                <br/>
                <xsl:value-of select="abstract" />
              </xsl:if>
            </li>
          </xsl:for-each>
        </ol>
      </li>
    </xsl:for-each>
  </ul>
  <xsl:call-template name="menubar" />
  <xsl:apply-templates select="/book/license" />
</xsl:template>

<!-- Part inside a book -->
<xsl:template match="/book/part">
  <xsl:if test="($chap != 0) and ($part = position())">
    <xsl:apply-templates select="chapter" />
  </xsl:if>
  <xsl:if test="($chap = 0) and ($part = position())">
    <xsl:choose>
      <xsl:when test="$style = 'printable'">
        <xsl:call-template name="printdoclayout" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="doclayout" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
</xsl:template>

<!-- Content of /book/part -->
<xsl:template name="bookpartcontent">
  <xsl:call-template name="menubar" />
  <h1><xsl:number level="multiple" format="1. " select="position()"/><xsl:value-of select="title" /></h1>
  <xsl:if test="abstract">
    <p><xsl:value-of select="abstract" /></p>
  </xsl:if>
  <p>Content:</p>
  <ol>
    <xsl:for-each select="chapter">
      <xsl:param name="curpos" select="position()" />
      <xsl:if test="title">
        <li>
          <b><a href="?part={$part}&amp;chap={$curpos}&amp;style={$style}"><xsl:value-of select="title" /></a></b>
          <xsl:if test="abstract">
            <br/><xsl:value-of select="abstract" />
          </xsl:if>
        </li>
      </xsl:if>
    </xsl:for-each>
  </ol>
  
  <xsl:call-template name="menubar" />
  <xsl:apply-templates select="/book/license" />
</xsl:template>

<!-- Menu bar -->
<xsl:template name="menubar">
  <xsl:variable name="prevpart" select="number($part) - 1" />
  <xsl:variable name="prevchap" select="number($chap) - 1" />
  <xsl:variable name="nextpart" select="number($part) + 1" />
  <xsl:variable name="nextchap" select="number($chap) + 1" />
  <xsl:if test="$style != 'printable'">
    <hr />
    <p class="alttext">
      <!-- Previous Parts -->
      <xsl:choose>
        <xsl:when test="number($prevpart) &lt; 1">
          [ &lt;&lt; Previous Part ]
        </xsl:when>
        <xsl:otherwise>
          [ <a href="?part={$prevpart}&amp;chap=0">&lt;&lt; Previous Part</a> ]
        </xsl:otherwise>
      </xsl:choose>
      <!-- Previous Chapter -->
      <xsl:choose>
        <xsl:when test="number($prevchap) &lt; 1">
          [ &lt; Previous Chapter ]
        </xsl:when>
        <xsl:otherwise>
          [ <a href="?part={$part}&amp;chap={$prevchap}">&lt; Previous Chapter</a> ]
        </xsl:otherwise>
      </xsl:choose>
      <!-- Content -->
      [ <a href="?part=0&amp;chap=0">Home</a> ]
      <!-- Next Chapter -->
      <xsl:if test="name() = 'book'">
        [ <a href="?part=1">Next Chapter &gt;</a> ]
      </xsl:if>
      <xsl:if test="name() = 'part'">
        [ <a href="?part={$part}&amp;chap=1">Next Chapter &gt;</a> ]
      </xsl:if>
      <xsl:if test="name() = 'chapter'">
        <xsl:choose>
          <xsl:when test="number($chap) = count(section)">
            [ Next Chapter &gt; ]
          </xsl:when>
          <xsl:otherwise>
            [ <a href="?part={$part}&amp;chap={$nextchap}">Next Chapter &gt;</a> ]
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <!-- Next Part -->
      <xsl:if test="name() = 'book'">
        [ <a href="?part={$nextpart}">Next Part &gt;&gt;</a> ]
      </xsl:if>
      <xsl:if test="name() = 'part'">
        <xsl:choose>
          <xsl:when test="number($part) = last()">
            [ Next Part &gt;&gt; ]
          </xsl:when>
          <xsl:otherwise>
            [ <a href="?part={$nextpart}&amp;chap=0">Next Part &gt;&gt;</a> ]
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <xsl:if test="name() = 'chapter'">
        <xsl:choose>
          <xsl:when test="count(/book/part) = number($part)">
            [ Next Part &gt;&gt; ] 
          </xsl:when>
          <xsl:otherwise>
            [ <a href="?part={$nextpart}&amp;chap=0">Next Part &gt;&gt;</a> ]
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </p>
    <hr />
  </xsl:if>
</xsl:template>


<!-- Chapter inside a part -->
<xsl:template match="/book/part/chapter">
  <xsl:if test="$chap = position()">
    <xsl:choose>
      <xsl:when test="$style = 'printable'">
        <xsl:call-template name="printdoclayout" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="doclayout" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
</xsl:template>

<!-- Content of /book/part/chapter -->
<xsl:template name="bookpartchaptercontent">
  <xsl:call-template name="menubar" />
  <h1><xsl:number level="multiple" format="1. " select="position()"/><xsl:value-of select="title" /></h1>
  <xsl:variable name="doc" select="include/@href"/>
  <xsl:variable name="FILE" select="document($doc)" />
  <xsl:if test="$FILE/sections/section/title">
    <b>Content: </b>
    <ul>
      <xsl:for-each select="$FILE/sections/section/title">
        <xsl:param name="pos" select="position()" />
        <li><a href="#doc_chap{$pos}" class="altlink"><xsl:value-of select="." /></a></li>
      </xsl:for-each>
    </ul>
  </xsl:if>
  <xsl:apply-templates select="$FILE/sections/section" />
  
  <xsl:call-template name="menubar" />
  <xsl:apply-templates select="/book/license" />
</xsl:template>

<!-- Section inside a chapter -->
<xsl:template match="/sections/section">
  <xsl:param name="pos" select="position()" />
  <a name="doc_chap{$pos}"/>
  <xsl:if test="title">
    <p class="chaphead"><span class="chapnum"><xsl:value-of select="$chap" />.<xsl:number level="multiple" format="a. " select="position()" /></span><xsl:value-of select="title" /></p>
  </xsl:if>
  <xsl:apply-templates select="body|subsection">
    <xsl:with-param name="chpos" select="$pos"/>
  </xsl:apply-templates>
</xsl:template>

<!-- Subsubsection inside a section -->
<xsl:template match="/sections/section/subsection">
  <xsl:param name="pos" select="position()"/>
  <a name="doc_chap{$chpos}_sect{$pos}" />
  <p class="secthead"><xsl:value-of select="title" /></p>
  <xsl:apply-templates select="body" />
</xsl:template>

</xsl:stylesheet>
