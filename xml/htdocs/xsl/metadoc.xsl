<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:func="http://exslt.org/functions" extension-element-prefixes="func" >

<xsl:template match="dynamic">
  <xsl:variable name="metadoc"><xsl:value-of select="@metadoc"/></xsl:variable>
<mainpage id="docs">
  <title><xsl:value-of select="title"/></title>
  <author title="Author">Gentoo Documentation Project</author>
  <version>Dynamically</version>
  <date>Dynamically</date>
 
  <chapter>
    <title><xsl:value-of select="title"/></title>
    <xsl:apply-templates match="intro"/>
  </chapter>

  <xsl:apply-templates>
    <xsl:with-param name="metadoc" select="$metadoc"/>
  </xsl:apply-templates>
</mainpage>
</xsl:template>

<xsl:template match="catid">
  <xsl:param name="metadoc"/>
  <xsl:variable name="categorie"><xsl:value-of select="text()"/></xsl:variable>
  <chapter>
    <title><xsl:value-of select="document($metadoc)/metadoc/categories/cat[@id = $categorie]"/></title>
    <xsl:call-template name="categories">
      <xsl:with-param name="metadoc" select="$metadoc"/>
      <xsl:with-param name="categorie" select="$categorie"/>
    </xsl:call-template>
  </chapter>
</xsl:template>

<xsl:template match="intro">
<xsl:copy-of select="@*|node()"/>
</xsl:template>

<xsl:template name="categories">
  <xsl:param name="metadoc"/>
  <xsl:param name="categorie"/>
  <!-- Non parental categories -->
  <xsl:if test="document($metadoc)/metadoc/docs/doc[memberof = $categorie]">
  <section>
  <body>
 
    <xsl:for-each select="document($metadoc)/metadoc/docs/doc[memberof = $categorie]">
      <xsl:call-template name="document">
        <xsl:with-param name="metadoc" select="$metadoc"/>
        <xsl:with-param name="fileid"  select="fileid/text()"/>
        <xsl:with-param name="vpart"   select="fileid/@vpart"/>
        <xsl:with-param name="vchap"   select="fileid/@vchap"/>
      </xsl:call-template>
    </xsl:for-each>
  
  </body>
  </section>
  </xsl:if>

  <!-- Parental categories -->
  <xsl:for-each select="document($metadoc)/metadoc/categories/cat[@parent = $categorie]">
    <xsl:variable name="currentcat"><xsl:value-of select="@id"/></xsl:variable>
    <section>
      <title><xsl:value-of select="text()"/></title>
      <body>

        <xsl:for-each select="document($metadoc)/metadoc/docs/doc[memberof = $currentcat]">
          <xsl:call-template name="document">
            <xsl:with-param name="metadoc"  select="$metadoc"/>
            <xsl:with-param name="fileid"   select="fileid/text()"/>
            <xsl:with-param name="vpart"    select="fileid/@vpart"/>
            <xsl:with-param name="vchap"    select="fileid/@vchap"/>
          </xsl:call-template>
        </xsl:for-each>
      
      </body>
    </section>
  </xsl:for-each>
</xsl:template>

<xsl:template name="document">
  <xsl:param name="metadoc"/>
  <xsl:param name="fileid"/>
  <xsl:param name="vpart"/>
  <xsl:param name="vchap"/>
  <xsl:variable name="link"><xsl:value-of select="document($metadoc)/metadoc/files/file[@id = $fileid]/text()"/></xsl:variable>

  <xsl:choose>
    <xsl:when test="$vpart">
      <xsl:choose>
        <xsl:when test="$vchap">
          <p><b><uri link="{$link}?part={$vpart}&amp;chap={$vchap}"><xsl:value-of select="document($link)/book/part[position()=$vpart]/chapter[position()=$vchap]/title"/></uri></b>: <xsl:value-of select="document($link)/book/part[position()=$vpart]/chapter[position()=$vchap]/abstract"/></p>
        </xsl:when>
        <xsl:otherwise>
          <p><b><uri link="{$link}?part={$vpart}"><xsl:value-of select="document($link)/book/part[position() = $vpart]/title"/></uri></b>: <xsl:value-of select="document($link)/book/part[position() = $vpart]/abstract"/></p>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <p><b><uri link="{$link}"><xsl:value-of select="document($link)/guide/title|document($link)/book/title|document($link)/mainpage/title"/></uri></b><xsl:if test="not(document($link)/mainpage)">: <xsl:value-of select="document($link)/guide/abstract|document($link)/book/abstract"/></xsl:if></p>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="listing">
  <xsl:param name="metadoc"/>
  <chapter>
  <title>Gentoo Documentation Overview</title>
  <section>
  <body>

  <xsl:for-each select="list">
    <xsl:call-template name="list">
      <xsl:with-param name="metadoc" select="$metadoc"/>
      <xsl:with-param name="catid"   select="text()"/>
    </xsl:call-template>
  </xsl:for-each>

  </body>
  </section>
  </chapter>
</xsl:template>

<xsl:template match="list" name="list">
  <xsl:param name="metadoc"/>
  <xsl:param name="catid" select="text()"/>
  <ul><b><xsl:value-of select="document($metadoc)/metadoc/categories/cat[@id = $catid]"/></b>
    <xsl:for-each select="document($metadoc)/metadoc/docs/doc[memberof = $catid]">
      <xsl:call-template name="linkfile">
        <xsl:with-param name="metadoc" select="$metadoc"/>
        <xsl:with-param name="fileid"  select="fileid"/>
        <xsl:with-param name="vpart"   select="fileid/@vpart"/>
        <xsl:with-param name="vchap"   select="fileid/@vchap"/>
      </xsl:call-template>
    </xsl:for-each>
    <xsl:for-each select="document($metadoc)/metadoc/categories/cat[@parent = $catid]">
      <xsl:call-template name="list">
        <xsl:with-param name="metadoc" select="$metadoc"/>
        <xsl:with-param name="catid"   select="@id"/>
      </xsl:call-template>
    </xsl:for-each>
  </ul>
</xsl:template>

<xsl:template name="linkfile">
  <xsl:param name="metadoc"/>
  <xsl:param name="fileid"/>
  <xsl:param name="vpart"/>
  <xsl:param name="vchap"/>
  
  <xsl:variable name="filelink"  select="document($metadoc)/metadoc/files/file[@id = $fileid]"/>
  <xsl:choose>
    <xsl:when test="$vpart">
      <xsl:choose>
        <xsl:when test="$vchap">
          <xsl:variable name="filetitle" select="document($filelink)/book/part[position() = $vpart]/chapter[position() = $vchap]/title"/>
          <li><uri link="{$filelink}?part={$vpart}&amp;chap={$vchap}"><xsl:value-of select="$filetitle"/></uri></li>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="filetitle" select="document($filelink)/book/part[position() = $vpart]/title"/>
          <li><uri link="{$filelink}?part={$vpart}"><xsl:value-of select="$filetitle"/></uri></li>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <xsl:variable name="filetitle" select="document($filelink)/guide/title|document($filelink)/book/title|document($filelink)/mainpage/title"/>
      <li><uri link="{$filelink}"><xsl:value-of select="$filetitle"/></uri></li>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="overview">
  <xsl:param name="metadoc"/>
  <chapter>
  <title>Files</title>
  <section>
  <body>

  <table>
  <tr>
    <th>Filename</th><th>Version</th><th>Master Version</th><th>Editing</th>
  </tr>
  <xsl:for-each select="document($metadoc)/metadoc/files/file">
  <xsl:variable name="fileurl" select="text()"/>
  <xsl:variable name="fileid"  select="@id"/>
  <xsl:variable name="parentmetadoc" select="@parent"/>
  <tr>
    <ti><uri link="{$fileurl}"><xsl:value-of select="$fileurl"/></uri></ti>
    <xsl:variable name="version"><xsl:value-of select="document($fileurl)/guide/version|document($fileurl)/book/version|document($fileurl)/sections/version|document($fileurl)/mainpage/version"/></xsl:variable>
    <ti><xsl:value-of select="$version"/></ti>
    <ti>
      <xsl:choose>
        <xsl:when test="document($parentmetadoc)/metadoc/files/file[@id = $fileid]">
          <xsl:variable name="parentfile" select="document($parentmetadoc)/metadoc/files/file[@id = $fileid]"/>
          <xsl:variable name="parentversion"><xsl:value-of select="document($parentfile)/guide/version|document($parentfile)/book/version|document($parentfile)/sections/version|document($parentfile)/mainpage/version"/></xsl:variable>
          <xsl:value-of select="$parentversion"/>
        </xsl:when>
        <xsl:otherwise>
          N/A
        </xsl:otherwise>
      </xsl:choose>
    </ti>
    <ti></ti>
  </tr>
  </xsl:for-each>
  </table>

  </body>
  </section>
  </chapter>
</xsl:template>

</xsl:stylesheet>
