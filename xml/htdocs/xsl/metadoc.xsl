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
      <xsl:choose>
        <xsl:when test="bugs/bug[@stopper = 'yes']">
          <!-- Ignore showstopper -->
        </xsl:when>
        <xsl:otherwise>
          <p><b>
          <xsl:call-template name="documentname">
            <xsl:with-param name="metadoc" select="$metadoc"/>
            <xsl:with-param name="fileid"  select="fileid/text()"/>
            <xsl:with-param name="vpart"   select="fileid/@vpart"/>
            <xsl:with-param name="vchap"   select="fileid/@vchap"/>
            <xsl:with-param name="docid"   select="@id"/>
          </xsl:call-template>
          </b>: <xsl:call-template name="documentabstract">
            <xsl:with-param name="metadoc" select="$metadoc"/>
            <xsl:with-param name="fileid"  select="fileid/text()"/>
            <xsl:with-param name="vpart"   select="fileid/@vpart"/>
            <xsl:with-param name="vchap"   select="fileid/@vchap"/>
            <xsl:with-param name="docid"   select="@id"/>
          </xsl:call-template>
          </p>
        </xsl:otherwise>
      </xsl:choose>
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
          <xsl:choose>
            <xsl:when test="bugs/bug[@stopper = 'yes']">

            </xsl:when>
            <xsl:otherwise>
              <p><b>
              <xsl:call-template name="documentname">
                <xsl:with-param name="metadoc"  select="$metadoc"/>
                <xsl:with-param name="fileid"   select="fileid/text()"/>
                <xsl:with-param name="vpart"    select="fileid/@vpart"/>
                <xsl:with-param name="vchap"    select="fileid/@vchap"/>
                <xsl:with-param name="docid"    select="@id"/>
              </xsl:call-template>
              </b>: <xsl:call-template name="documentabstract">
                <xsl:with-param name="metadoc"  select="$metadoc"/>
                <xsl:with-param name="fileid"   select="fileid/text()"/>
                <xsl:with-param name="vpart"    select="fileid/@vpart"/>
                <xsl:with-param name="vchap"    select="fileid/@vchap"/>
                <xsl:with-param name="docid"    select="@id"/>
              </xsl:call-template>
              </p>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
      
      </body>
    </section>
  </xsl:for-each>
</xsl:template>

<xsl:template name="documentname">
  <xsl:param name="metadoc"/>
  <xsl:param name="fileid"/>
  <xsl:param name="vpart"/>
  <xsl:param name="vchap"/>
  <xsl:param name="docid"/>
  <xsl:variable name="link"><xsl:value-of select="document($metadoc)/metadoc/files/file[@id = $fileid]/text()"/></xsl:variable>

  <xsl:choose>
    <xsl:when test="$vpart">
      <xsl:choose>
        <xsl:when test="$vchap">
          <uri link="{$link}?part={$vpart}&amp;chap={$vchap}"><xsl:value-of select="document($link)/book/part[position()=$vpart]/chapter[position()=$vchap]/title"/></uri>
        </xsl:when>
        <xsl:otherwise>
          <uri link="{$link}?part={$vpart}"><xsl:value-of select="document($link)/book/part[position() = $vpart]/title"/></uri>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <uri link="{$link}"><xsl:value-of select="document($link)/guide/title|document($link)/book/title|document($link)/mainpage/title"/></uri>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="documentabstract">
  <xsl:param name="metadoc"/>
  <xsl:param name="fileid"/>
  <xsl:param name="vpart"/>
  <xsl:param name="vchap"/>
  <xsl:param name="docid"/>
  <xsl:variable name="link"><xsl:value-of select="document($metadoc)/metadoc/files/file[@id = $fileid]/text()"/></xsl:variable>

  <xsl:choose>
    <xsl:when test="$vpart">
      <xsl:choose>
        <xsl:when test="$vchap">
          <xsl:value-of select="document($link)/book/part[position()=$vpart]/chapter[position()=$vchap]/abstract"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="document($link)/book/part[position() = $vpart]/abstract"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <xsl:if test="not(document($link)/mainpage)"><xsl:value-of select="document($link)/guide/abstract|document($link)/book/abstract"/></xsl:if>
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
      <xsl:choose>
        <xsl:when test="bugs/bug[@stopper = 'yes']">
          <!-- Ignore showstopper case -->
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="documentname">
            <xsl:with-param name="metadoc" select="$metadoc"/>
            <xsl:with-param name="fileid"  select="fileid"/>
            <xsl:with-param name="vpart"   select="fileid/@vpart"/>
            <xsl:with-param name="vchap"   select="fileid/@vchap"/>
            <xsl:with-param name="docid"   select="@id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:for-each select="document($metadoc)/metadoc/categories/cat[@parent = $catid]">
      <xsl:call-template name="list">
        <xsl:with-param name="metadoc" select="$metadoc"/>
        <xsl:with-param name="catid"   select="@id"/>
      </xsl:call-template>
    </xsl:for-each>
  </ul>
</xsl:template>

<xsl:template match="overview">
  <xsl:param name="metadoc"/>
  <chapter id="files">
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

  <chapter id="bugs">
  <title>Bugs</title>
  <section id="showstoppers">
  <title>Showstoppers</title>
  <body>

  <table>
  <tr><th>Document</th><th>Bug ID</th></tr>
  <xsl:for-each select="document($metadoc)/metadoc/docs/doc[bugs/bug/@stopper = 'yes']">
    <tr>
      <ti>
        <xsl:call-template name="documentname">
          <xsl:with-param name="metadoc" select="$metadoc"/>
          <xsl:with-param name="fileid"  select="fileid/text()"/>
          <xsl:with-param name="vpart"   select="fileid/@vpart"/>
          <xsl:with-param name="vchap"   select="fileid/@vchap"/>
          <xsl:with-param name="docid"   select="@id"/>
        </xsl:call-template>
      </ti>
      <ti>
        <xsl:for-each select="bugs/bug[@stopper = 'yes']">
          <xsl:variable name="bugid" select="text()"/>
          <uri link="http://bugs.gentoo.org/show_bug.cgi?id={$bugid}">
            <xsl:value-of select="$bugid"/>
          </uri>
          <xsl:if test="not(position() = last())">, </xsl:if>
        </xsl:for-each>
      </ti>
    </tr>
  </xsl:for-each>
  </table>

  </body>
  </section>
  <section id="normalbugs">
  <title>Normal Bugs</title>
  <body>

  <table>
  <tr><th>Document</th><th>Bug ID</th></tr>
  <xsl:for-each select="document($metadoc)/metadoc/docs/doc[bugs/bug[not(@stopper = 'yes')]]">
    <tr>
      <ti>
        <xsl:call-template name="documentname">
          <xsl:with-param name="metadoc" select="$metadoc"/>
          <xsl:with-param name="fileid"  select="fileid/text()"/>
          <xsl:with-param name="vpart"   select="fileid/@vpart"/>
          <xsl:with-param name="vchap"   select="fileid/@vchap"/>
          <xsl:with-param name="docid"   select="@id"/>
        </xsl:call-template>
      </ti>
      <ti>
        <xsl:for-each select="bugs/bug[not(@stopper = 'yes')]">
          <xsl:variable name="bugid" select="text()"/>
          <uri link="http://bugs.gentoo.org/show_bug.cgi?id={$bugid}">
            <xsl:value-of select="$bugid"/>
          </uri>
          <xsl:if test="not(position() = last())">, </xsl:if>
        </xsl:for-each>
      </ti>
    </tr>
  </xsl:for-each>
  </table>

  </body>
  </section>
  </chapter>
</xsl:template>

</xsl:stylesheet>
