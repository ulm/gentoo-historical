<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!-- Define global variables; if a user has
     already defined those, this is a NOP -->
<xsl:param name="chap">0</xsl:param>
<xsl:param name="sect">0</xsl:param>

<!-- A book -->
<xsl:template match="/book">
  <!-- If chap = 0, show an index -->
  <xsl:choose>
    <xsl:when test="$chap != 0">
      <xsl:apply-templates select="chapter" />
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
    <xsl:for-each select="chapter">
      <xsl:param name="curchap" select="position()" />
      <li>
        <a href="?chap={$curchap}&amp;sect=0&amp;style={$style}" class="menulink"><xsl:value-of select="title" /></a>
        <xsl:if test="abstract">
          <br/>
          <p><xsl:value-of select="abstract" /></p>
        </xsl:if>
        <ul>
          <xsl:for-each select="section">
            <xsl:param name="cursect" select="position()" />
            <li>
              <a href="?chap={$curchap}&amp;sect={$cursect}&amp;style={$style}" class="menulink"><xsl:value-of select="title" /></a>
              <xsl:if test="abstract">
                <br/>
                <p><xsl:value-of select="abstract" /></p>
              </xsl:if>
            </li>
          </xsl:for-each>
        </ul>
      </li>
    </xsl:for-each>
  </ul>
  <xsl:call-template name="menubar" />
</xsl:template>

<!-- Chapter inside a book -->
<xsl:template match="/book/chapter">
  <xsl:if test="($sect != 0) and ($chap = position())">
    <xsl:apply-templates select="section" />
  </xsl:if>
  <xsl:if test="($sect = 0) and ($chap = position())">
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

<!-- Content of /book/chapter -->
<xsl:template name="bookchaptercontent">
  <xsl:call-template name="menubar" />
  <h1><xsl:number level="multiple" format="1. " select="position()"/><xsl:value-of select="title" /></h1>
  <xsl:if test="abstract">
    <p><xsl:value-of select="abstract" /></p>
  </xsl:if>
  <p>Content:</p>
  <ul>
    <xsl:for-each select="section">
      <xsl:param name="curpos" select="position()" />
      <xsl:if test="title">
        <li>
          <a href="?chap={$chap}&amp;sect={$curpos}&amp;style={$style}"><xsl:value-of select="title" /></a>
          <xsl:if test="abstract">
            <br/><p><xsl:value-of select="abstract" /></p>
          </xsl:if>
        </li>
      </xsl:if>
    </xsl:for-each>
  </ul>
  
  <xsl:call-template name="menubar" />
</xsl:template>

<!-- Menu bar -->
<xsl:template name="menubar">
  <xsl:variable name="prevchap" select="number($chap) - 1" />
  <xsl:variable name="prevsect" select="number($sect) - 1" />
  <xsl:variable name="nextchap" select="number($chap) + 1" />
  <xsl:variable name="nextsect" select="number($sect) + 1" />
  <xsl:if test="$style != 'printable'">
    <hr />
    <p class="alttext">
      <!-- Previous Chapters -->
      <xsl:choose>
        <xsl:when test="number($prevchap) &lt; 1">
          [ &lt;&lt; Previous Chapter ]
        </xsl:when>
        <xsl:otherwise>
          [ <a href="?chap={$prevchap}&amp;sect=0">&lt;&lt; Previous Chapter</a> ]
        </xsl:otherwise>
      </xsl:choose>
      <!-- Previous Sections -->
      <xsl:choose>
        <xsl:when test="number($prevsect) &lt; 1">
          [ &lt; Previous Section ]
        </xsl:when>
        <xsl:otherwise>
          [ <a href="?chap={$chap}&amp;sect={$prevsect}">&lt; Previous Section</a> ]
        </xsl:otherwise>
      </xsl:choose>
      <!-- Content -->
      [ <a href="?chap=0&amp;sect=0">Home</a> ]
      <!-- Next Section -->
      <xsl:if test="chapter">
        [ Next Section &gt; ]
      </xsl:if>
      <xsl:if test="section">
        <xsl:choose>
          <xsl:when test="number($sect) = count(section)">
            [ Next Section &gt; ]
          </xsl:when>
          <xsl:otherwise>
            [ <a href="?chap={$chap}&amp;sect={$nextsect}">Next Section &gt;</a> ]
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <xsl:if test="subsection">
        <xsl:choose>
          <xsl:when test="number($sect) = last()">
            [ Next Section &gt; ]
          </xsl:when>
          <xsl:otherwise>
            [ <a href="?chap={$chap}&amp;sect={$nextsect}">Next Section &gt;</a> ]
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <!-- Next Chapter -->
      <xsl:if test="chapter">
        [ <a href="?chap={$nextchap}&amp;sect=0">Next Chapter &gt;&gt;</a> ]
      </xsl:if>
      <xsl:if test="section">
        <xsl:choose>
          <xsl:when test="number($chap) = last()">
            [ Next Chapter &gt;&gt; ] 
          </xsl:when>
          <xsl:otherwise>
            [ <a href="?chap={$nextchap}&amp;sect=0">Next Chapter &gt;&gt;</a> ]
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <xsl:if test="subsection">
        <xsl:choose>
          <xsl:when test="number($chap) = count(/book/chapter)">
            [ Next Chapter &gt;&gt; ]
          </xsl:when>
          <xsl:otherwise>
            [ <a href="?chap={$nextchap}&amp;sect=0">Next Chapter &gt;&gt;</a> ]
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </p>
    <hr />
  </xsl:if>
</xsl:template>


<!-- Section inside a chapter -->
<xsl:template match="/book/chapter/section">
  <xsl:if test="$sect = position()">
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

<!-- Content of /book/chapter/section -->
<xsl:template name="bookchaptersectioncontent">
  <xsl:call-template name="menubar" />
  <h1><xsl:number level="multiple" format="1. " select="position()"/><xsl:value-of select="title" /></h1>
  <xsl:if test="subsection/title">
    <b>Content: </b>
    <ul>
      <xsl:for-each select="subsection/title">
        <xsl:param name="pos" select="position()" />
        <li><a href="#{$pos}" class="altlink"><xsl:value-of select="." /></a></li>
      </xsl:for-each>
    </ul>
  </xsl:if>
  <xsl:apply-templates select="body|subsection" />
  
  <xsl:call-template name="menubar" />
</xsl:template>

<!-- Subsection inside a section -->
<xsl:template match="/book/chapter/section/subsection">
  <xsl:param name="pos" select="position()" />
  <a name="{$pos}"/>
  <xsl:if test="title">
    <h2 class="secthead"><xsl:value-of select="$sect" />.<xsl:number level="multiple" format="a. " select="position()" /><xsl:value-of select="title" /></h2>
  </xsl:if>
  <xsl:apply-templates select="body|subsubsection" />
</xsl:template>

<!-- Subsubsection inside a subsection -->
<xsl:template match="/book/chapter/section/subsection/subsubsection">
  <h3 class="subsecthead"><xsl:value-of select="title" /></h3>
  <xsl:apply-templates select="body" />
</xsl:template>

</xsl:stylesheet>
