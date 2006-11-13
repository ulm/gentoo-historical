<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" 
                xmlns:exslt="http://exslt.org/common"
                xmlns:math="http://exslt.org/math"
                extension-element-prefixes="exslt math">
<xsl:output method="text" indent="no"/>
<xsl:strip-space elements="*"/>
<xsl:preserve-space elements="pre"/>

<xsl:param name="wrap-pos" select="'77'"/>

<xsl:param name="lang" select="/guide/@lang"/>

<!-- Define inserted strings per @lang here to avoid all the inserts.xsl foo -->
<xsl:variable name="STRINGS">
  <strings lang="en">
    <string id="note">Note:</string>
    <string id="warn">Warning:</string>
    <string id="impo">Important:</string>
    <string id="figure">Figure</string>
    <string id="pre">Code Listing</string>
  </strings>
  <strings lang="fr">
    <string id="note">Note :</string>
    <string id="warn">Avertissement :</string>
    <string id="impo">Important :</string>
    <string id="figure">Figure</string>
    <string id="pre">Exemple de code</string>
  </strings>
</xsl:variable>

<!-- Collect all links that should be numbered -->
<xsl:variable name="all-links">
  <links>
    <xsl:for-each select="//uri[@link]|//mail[@link]">
      <xsl:if test="not(starts-with(@link, '#')) and not(starts-with(@link, '?')) and not(@link=normalize-space(.)) and not(name(..)='author')">
        <uri>
          <xsl:attribute name="id"><xsl:value-of select="generate-id(.)"/></xsl:attribute>
          <xsl:choose>
            <xsl:when test="starts-with(@link, '/')">
              <xsl:value-of select="concat('http://www.gentoo.org',@link)"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="@link"/>
            </xsl:otherwise>
          </xsl:choose>
        </uri>
      </xsl:if>
    </xsl:for-each>
  </links>
</xsl:variable>

<!-- Number unique links -->
<xsl:variable name="unique-links">
  <links>
    <xsl:for-each select="exslt:node-set($all-links)/*[1]/*[not(text()=preceding-sibling::*/text())]">
      <uri pos="{position()}"><xsl:value-of select="."/></uri>
    </xsl:for-each>
  </links>
</xsl:variable>


<xsl:template match="guide">
  <xsl:variable name="header">
    <xsl:text>&#xA;</xsl:text>
    <xsl:call-template name="wrap-text">
      <xsl:with-param name="txt" select="normalize-space(title)"/>
    </xsl:call-template>
    <xsl:text>&#xA;http://www.gentoo.org/news/</xsl:text><xsl:value-of select="$lang"/><xsl:text>/gwn/current.xml&#xA;</xsl:text>
    <xsl:call-template name="wrap-text">
      <xsl:with-param name="txt" select="normalize-space(abstract)"/>
    </xsl:call-template>
    <xsl:text>&#xA;</xsl:text>
  </xsl:variable>

  <xsl:variable name="header-width">
    <xsl:call-template name="longest-line-width">
      <xsl:with-param name="txt" select="$header"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:call-template name="repeat">
    <xsl:with-param name="N" select="$header-width"/>
    <xsl:with-param name="txt" select="'~'"/>
  </xsl:call-template>

  <xsl:value-of select="$header"/>

  <xsl:call-template name="repeat">
    <xsl:with-param name="N" select="$header-width"/>
    <xsl:with-param name="txt" select="'~'"/>
  </xsl:call-template>

  <xsl:text>&#xA;</xsl:text>
  <xsl:apply-templates select="chapter"/>
  <xsl:text>&#xA;</xsl:text>

  <xsl:for-each select="author">
    <xsl:value-of select="mail"/><xsl:text> &lt;</xsl:text><xsl:value-of select="mail/@link"/>
    <xsl:text>&gt; - </xsl:text><xsl:value-of select="@title"/>
    <xsl:if test="position() != last()">
      <xsl:text>&#xA;</xsl:text>
    </xsl:if>
  </xsl:for-each>
</xsl:template>

<xsl:template match="chapter">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="chapter/title">
  <xsl:variable name="t">
    <xsl:call-template name="wrap-text">
      <xsl:with-param name="txt">
        <xsl:number level="any" count="//chapter/title"/>. <xsl:value-of select="normalize-space(.)"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="title-width">
    <xsl:call-template name="longest-line-width">
      <xsl:with-param name="txt" select="$t"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:text>&#xA;</xsl:text>

  <xsl:call-template name="repeat">
    <xsl:with-param name="N" select="$title-width"/>
    <xsl:with-param name="txt" select="'='"/>
  </xsl:call-template>
  <xsl:text>&#xA;</xsl:text>

  <xsl:value-of select="$t"/>
  <xsl:text>&#xA;</xsl:text>

  <xsl:call-template name="repeat">
    <xsl:with-param name="N" select="$title-width"/>
    <xsl:with-param name="txt" select="'='"/>
  </xsl:call-template>

  <xsl:text>&#xA;</xsl:text>
</xsl:template>


<xsl:template match="section">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="section/title">
  <xsl:variable name="t">
    <xsl:call-template name="wrap-text">
      <xsl:with-param name="txt" select="normalize-space(.)"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="title-width">
    <xsl:call-template name="longest-line-width">
      <xsl:with-param name="txt" select="$t"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:text>&#xA;</xsl:text>

  <xsl:value-of select="$t"/>
  <xsl:text>&#xA;</xsl:text>

  <xsl:call-template name="repeat">
    <xsl:with-param name="N" select="$title-width"/>
    <xsl:with-param name="txt" select="'-'"/>
  </xsl:call-template>

  <xsl:text>&#xA;</xsl:text>
</xsl:template>


<xsl:template match="body">
  <xsl:apply-templates/>
</xsl:template>


<xsl:template match="p|note|impo|warn">
  <xsl:text>&#xA;</xsl:text>
  <xsl:variable name="p">
    <xsl:if test="name(.) != 'p'">
      <xsl:variable name="N"><xsl:value-of select="name(.)"/></xsl:variable>
      <xsl:value-of select="exslt:node-set($STRINGS)//strings[@lang=$lang]/string[@id=$N]"/>
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
  </xsl:variable>
  <xsl:call-template name="wrap-text">
    <xsl:with-param name="txt" select="normalize-space($p)"/>
  </xsl:call-template>
  <xsl:text>&#xA;</xsl:text>

  <xsl:variable name="footer">
    <xsl:apply-templates select=".//uri|.//mail" mode="footer"/>
  </xsl:variable>
  <xsl:if test="string-length($footer)>0">
    <xsl:text>&#xA;</xsl:text>
    <xsl:call-template name="display-footer">
      <xsl:with-param name="footer" select="$footer"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>


<xsl:template match="table">
  <xsl:variable name="widths">
    <xsl:for-each select="tr[1]/th | tr[1]/ti">
      <xsl:variable name="P" select="position()"/>
      <xsl:variable name="lengths">
        <xsl:for-each select="../../tr/*[position()=$P]">
          <xsl:variable name="col"><xsl:apply-templates/></xsl:variable>
          <length><xsl:value-of select="string-length($col)"/></length>
        </xsl:for-each>
      </xsl:variable>
      <width><xsl:value-of select="math:max(exslt:node-set($lengths)/*)"/></width>
    </xsl:for-each>
  </xsl:variable>

  <xsl:apply-templates>
    <xsl:with-param name="widths" select="$widths"/>
  </xsl:apply-templates>

  <xsl:text>&#xA;</xsl:text>

  <xsl:variable name="footer">
    <xsl:apply-templates select=".//uri|.//mail" mode="footer"/>
  </xsl:variable>
  <xsl:if test="string-length($footer)>0">
    <xsl:text>&#xA;</xsl:text>
    <xsl:call-template name="display-footer">
      <xsl:with-param name="footer" select="$footer"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>

<xsl:template match="tr">
<xsl:param name="widths"/>
  <xsl:text>&#xA;</xsl:text>
  <xsl:apply-templates select="ti|th">
    <xsl:with-param name="widths" select="$widths"/>
  </xsl:apply-templates>
</xsl:template>

<xsl:template match="th|ti">
<xsl:param name="widths"/>
  <xsl:variable name="P" select="position()"/>
  <xsl:variable name="coltxt"><xsl:apply-templates/></xsl:variable>
  <xsl:value-of select="$coltxt"/>
  <xsl:if test="position() != last()">
    <xsl:call-template name="repeat">
      <xsl:with-param name="txt" select="' '"/>
      <xsl:with-param name="N" select="1 + number(exslt:node-set($widths)/width[position()=$P]) - string-length($coltxt)"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>


<xsl:template match="ul">
  <xsl:text>&#xA;</xsl:text>
  <xsl:apply-templates/>

  <xsl:variable name="footer">
    <xsl:apply-templates select=".//uri|.//mail" mode="footer"/>
  </xsl:variable>
  <xsl:if test="string-length($footer)>0">
    <xsl:text>&#xA;</xsl:text>
    <xsl:call-template name="display-footer">
      <xsl:with-param name="footer" select="$footer"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>


<xsl:template match="li">
  <xsl:variable name="li">
    <xsl:apply-templates/>
  </xsl:variable>

  <xsl:text>  * </xsl:text>
  <xsl:call-template name="wrap-text">
    <xsl:with-param name="txt" select="normalize-space($li)"/>
    <xsl:with-param name="indent" select="'4'"/>
    <xsl:with-param name="curcol" select="'4'"/>
  </xsl:call-template>
  <xsl:text>&#xA;</xsl:text>
</xsl:template>


<xsl:template match="uri|mail">
  <xsl:variable name="this"><xsl:value-of select="generate-id(.)"/></xsl:variable>

  <xsl:value-of select="normalize-space(.)"/>
  <xsl:if test="exslt:node-set($all-links)//uri[@id=$this]">
    <xsl:variable name="link">
      <xsl:value-of select="exslt:node-set($all-links)//uri[@id=$this]"/>
    </xsl:variable>
    <xsl:text>[</xsl:text>
    <xsl:value-of select="exslt:node-set($unique-links)//uri[text()=$link]/@pos"/>
    <xsl:text>]</xsl:text>
  </xsl:if>
</xsl:template>

<xsl:template match="uri|mail" mode="footer">
  <xsl:variable name="this"><xsl:value-of select="generate-id(.)"/></xsl:variable>

  <xsl:if test="exslt:node-set($all-links)//uri[@id=$this]">
    <xsl:variable name="link">
      <xsl:value-of select="exslt:node-set($all-links)//uri[@id=$this]"/>
    </xsl:variable>
    <footlink>
      <pos><xsl:value-of select="exslt:node-set($unique-links)//uri[text()=$link]/@pos"/></pos>
      <link><xsl:value-of select="$link"/></link>
    </footlink>
  </xsl:if>
</xsl:template>

<xsl:template name="display-footer">
<xsl:param name="footer"/>
  <xsl:for-each select="exslt:node-set($footer)/footlink[not(pos/text()=following::pos/text())]">
  <xsl:sort select="pos" data-type="number"/>
    <xsl:value-of select="concat(substring('      ',1,4-string-length(pos)), pos)"/>
    <xsl:text>. </xsl:text>
    <xsl:value-of select="link"/>
    <xsl:text>&#xA;</xsl:text>
  </xsl:for-each>
</xsl:template>

<xsl:template match="figure">
  <xsl:variable name="Link">
    <xsl:choose>
      <xsl:when test="starts-with(@link, '/')">
        <xsl:value-of select="concat('http://www.gentoo.org',@link)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@link"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:text>&#xA;</xsl:text>
  <xsl:call-template name="wrap-text">
    <xsl:with-param name="txt">
      <xsl:value-of select="exslt:node-set($STRINGS)//strings[@lang=$lang]/string[@id='figure']"/>
      <xsl:text> </xsl:text>
      <xsl:number count="//chapter"/><xsl:text>.</xsl:text><xsl:number level="single" count="figure"/>
      <xsl:text>: </xsl:text>
      <xsl:value-of select="normalize-space(@caption)"/>
    </xsl:with-param>
  </xsl:call-template>

  <xsl:text>&#xA;</xsl:text>
  <xsl:value-of select="$Link"/>
  <xsl:text>&#xA;</xsl:text>
</xsl:template>


<xsl:template match="pre">
  <xsl:variable name="tcode">
    <xsl:value-of select="."/>
  </xsl:variable>

  <xsl:variable name="code">
    <xsl:if test="substring($tcode,1,1)='&#xA;'"><xsl:value-of select="substring-after($tcode,'&#xA;')"/></xsl:if>
    <xsl:if test="substring($tcode,1,1)!='&#xA;'"><xsl:value-of select="$tcode"/></xsl:if>
  </xsl:variable>

  <xsl:variable name="code-width">
    <xsl:call-template name="longest-line-width">
      <xsl:with-param name="txt" select="$code"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="pre-width">
    <xsl:choose>
      <xsl:when test="(number($wrap-pos)-4) > number($code-width)">
        <xsl:value-of select="number($wrap-pos)-4"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="number($code-width)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="header">
    <xsl:value-of select="exslt:node-set($STRINGS)//strings[@lang=$lang]/string[@id='pre']"/>
    <xsl:text> </xsl:text>
    <xsl:number count="//chapter"/><xsl:text>.</xsl:text><xsl:number level="single" count="pre"/>
    <xsl:text>&#xA;</xsl:text>
    <xsl:call-template name="wrap-text">
      <xsl:with-param name="txt" select="normalize-space(@caption)"/>
      <xsl:with-param name="wrap-at" select="$pre-width"/>
    </xsl:call-template>
  </xsl:variable>

  <xsl:variable name="dashes">
    <xsl:text>+-</xsl:text>
      <xsl:call-template name="repeat">
        <xsl:with-param name="N" select="$pre-width"/>
        <xsl:with-param name="txt" select="'-'"/>
      </xsl:call-template>
    <xsl:text>-+</xsl:text>
  </xsl:variable>

  <xsl:text>&#xA;</xsl:text>
  <xsl:value-of select="$dashes"/>
  <xsl:text>&#xA;</xsl:text>
  
  <xsl:call-template name="decorate-pre">
    <xsl:with-param name="width" select="$pre-width"/>
    <xsl:with-param name="txt" select="$header"/>
  </xsl:call-template>
  
  <xsl:value-of select="$dashes"/>
  <xsl:text>&#xA;</xsl:text>

  <xsl:call-template name="decorate-pre">
    <xsl:with-param name="width" select="$pre-width"/>
    <xsl:with-param name="txt" select="$code"/>
  </xsl:call-template>

  <xsl:value-of select="$dashes"/>
  <xsl:text>&#xA;</xsl:text>
</xsl:template>


<xsl:template name="decorate-pre">
<xsl:param name="width"/>
<xsl:param name="txt"/>
  <xsl:variable name="line">
    <xsl:choose>
      <xsl:when test="contains($txt, '&#xA;')">
        <xsl:value-of select="substring-before($txt, '&#xA;')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$txt"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="rest">
    <xsl:if test="contains($txt, '&#xA;')">
      <xsl:value-of select="substring-after($txt, '&#xA;')"/>
    </xsl:if>
  </xsl:variable>

  <xsl:text>| </xsl:text>
  <xsl:value-of select="$line"/>
  <xsl:call-template name="repeat">
    <xsl:with-param name="N" select="number($width)-string-length($line)"/>
    <xsl:with-param name="txt" select="' '"/>
  </xsl:call-template>
  <xsl:text> |&#xA;</xsl:text>

  <xsl:if test="string-length($rest)>0">
    <xsl:call-template name="decorate-pre">
      <xsl:with-param name="width" select="$width"/>
      <xsl:with-param name="txt" select="$rest"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>


<xsl:template name="repeat">
<xsl:param name="txt"/>
<xsl:param name="N"/>
  <xsl:if test="number($N) > 0">
    <xsl:value-of select="$txt"/>
    <xsl:call-template name="repeat">
      <xsl:with-param name="txt" select="$txt"/>
      <xsl:with-param name="N" select="number($N)-1"/>
    </xsl:call-template>
  </xsl:if>
</xsl:template>


<xsl:template name="longest-line-width">
<xsl:param name="txt"/>
  <xsl:variable name="line-lengths">
    <xsl:call-template name="line-width">
      <xsl:with-param name="txt" select="$txt"/>
    </xsl:call-template>
  </xsl:variable>  
  <xsl:value-of select="math:max(exslt:node-set($line-lengths)/*)"/>
</xsl:template>

<xsl:template name="line-width">
<xsl:param name="txt"/>
  <xsl:choose>
    <xsl:when test="contains($txt, '&#xA;')">
      <xsl:element name="len"><xsl:value-of select="string-length(substring-before($txt,'&#xA;'))"/></xsl:element>
      <xsl:call-template name="line-width">
        <xsl:with-param name="txt" select="substring-after($txt,'&#xA;')"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:element name="len"><xsl:value-of select="string-length($txt)"/></xsl:element>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template name="wrap-text">
<xsl:param name="txt"/>
<xsl:param name="firstword" select="'1'"/>
<xsl:param name="curcol" select="'0'"/>
<xsl:param name="indent" select="'0'"/>
<xsl:param name="wrap-at" select="$wrap-pos"/>
  <xsl:if test="string-length($txt)>0">
    <xsl:variable name="word">
      <xsl:choose>
        <xsl:when test="contains($txt, ' ')">
          <xsl:value-of select="substring-before($txt, ' ')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$txt"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="rest">
      <xsl:if test="contains($txt, ' ')">
        <xsl:value-of select="substring-after($txt, ' ')"/>
      </xsl:if>
    </xsl:variable>

    <xsl:variable name="space">
      <xsl:if test="not($firstword='1')">
        <xsl:text> </xsl:text>
      </xsl:if>
    </xsl:variable>

    <xsl:choose>
      <xsl:when test="((number($indent) + number($curcol) + string-length($space) + string-length($word)) >= $wrap-at) and not($firstword='1')">
        <!-- Insert line break -->
        <xsl:text>&#xA;</xsl:text>
        <xsl:call-template name="repeat">
          <xsl:with-param name="N" select="$indent"/>
          <xsl:with-param name="txt" select="' '"/>
        </xsl:call-template>
        <xsl:value-of select="$word"/>
        <xsl:call-template name="wrap-text">
          <xsl:with-param name="firstword" select="'0'"/>
          <xsl:with-param name="txt" select="$rest"/>
          <xsl:with-param name="curcol" select="string-length($word)"/>
          <xsl:with-param name="indent" select="$indent"/>
          <xsl:with-param name="wrap-at" select="$wrap-at"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="concat($space, $word)"/>
        <xsl:call-template name="wrap-text">
          <xsl:with-param name="firstword" select="'0'"/>
          <xsl:with-param name="txt" select="$rest"/>
          <xsl:with-param name="curcol" select="number($curcol)+string-length(concat($space,$word))"/>
          <xsl:with-param name="indent" select="$indent"/>
          <xsl:with-param name="wrap-at" select="$wrap-at"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
</xsl:template>



<!-- Not used -->
<xsl:template name="uniq-lines">
<xsl:param name="txt"/>
<xsl:param name="prev-line"/>
  <xsl:choose>
    <xsl:when test="contains($txt, '&#xA;')">
      <xsl:variable name="line">
        <xsl:value-of select="substring-before($txt,'&#xA;')"/>
      </xsl:variable>
      <xsl:if test="$line != $prev-line">
        <xsl:value-of select="$line"/><xsl:text>&#xA;</xsl:text>
      </xsl:if>
      <xsl:call-template name="uniq-lines">
        <xsl:with-param name="txt" select="substring-after($txt,'&#xA;')"/>
        <xsl:with-param name="prev-line" select="$line"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:if test="$txt != $prev-line">
        <xsl:value-of select="$txt"/><xsl:text>&#xA;</xsl:text>
      </xsl:if>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


</xsl:stylesheet>
