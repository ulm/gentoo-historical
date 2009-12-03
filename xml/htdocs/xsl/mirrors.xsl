<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                xmlns:str="http://exslt.org/strings"
                extension-element-prefixes="str exslt">

<xsl:output     omit-xml-declaration="yes"
                indent="yes"
                cdata-section-elements="description"/>

<xsl:param name="mode"/>

<xsl:key name="country" match="/mirrors/countries/country" use="@code"/>

<xsl:strip-space elements="*"/>

<!-- Identity transform, just copy everything -->
<xsl:template match="/ | mirrors | /mirrors//* | mainpage | mainpage//* | @*">
 <xsl:copy>
  <xsl:apply-templates select="@*"/>
  <xsl:apply-templates/>
 </xsl:copy>
</xsl:template>

<xsl:template match="@country">
  <xsl:attribute name="country">
   <xsl:value-of select="."/>
  </xsl:attribute>
  <xsl:attribute name="countryname">
   <xsl:value-of select="key('country', .)"/>
  </xsl:attribute>
</xsl:template>

<xsl:template match="/mirrors/countries"/> <!-- Leave'em behind -->


<xsl:template match="/mainpage//mirrorlist">
 <!-- Given a XML file (@src) containing mirrors grouped by country,
	  generate list of mirrors, when (inside a mainpage && @select='full')
                                  || (inside a     body && @select='partial') 
								  -->
 <xsl:variable name="the-mirrors" select="document(@src)"/>

 <xsl:choose>
  <xsl:when test="name(..)='mainpage' and @select='full'">
   <xsl:for-each select="$the-mirrors//mirrorgroup">
    <xsl:variable name="r" select="@region"/>
    <xsl:if test="count(preceding-sibling::mirrorgroup[@region=$r])=0">
      <chapter id="{str:encode-uri(translate($r, ' ', ''),true())}">
        <title>
         <xsl:value-of select="@region"/>
        </title>
         <xsl:for-each select="$the-mirrors//mirrorgroup[@region=$r]">
         <xsl:sort select="key('country', @country)"/>
          <xsl:if test="mirror[uri[contains('nN',@partial)]]">
            <xsl:variable name="c" select="@country"/>
            <xsl:variable name="n" select="key('country', @country)"/>
            <section id="{str:encode-uri(translate($n, ' ', ''),true())}">
              <xsl:if test="count($the-mirrors//mirrorgroup[@region=$r])>1 or not($n=$r)">
               <title>
                <xsl:value-of select="$n"/>
               </title>
              </xsl:if>
              <body>
              <p>
               <xsl:for-each select="mirror[uri[contains('nN',@partial)]]">
               <xsl:sort select="translate(name,'qwertyuiopasdfghjklzxcvbnm','QWERTYUIOPASDFGHJKLZXCVBNM')"/>
                 <xsl:apply-templates select="uri[contains('nN',@partial)]" mode="mirror"/>
               </xsl:for-each>
              </p>
              </body>
            </section>
          </xsl:if>
         </xsl:for-each>
      </chapter>
    </xsl:if>
   </xsl:for-each>
  </xsl:when>
  <xsl:when test="name(..)='body' and @select='partial'">
   <xsl:for-each select="$the-mirrors//mirror[uri[contains('yY',@partial)]]">
   <xsl:sort select="translate(name,'qwertyuiopasdfghjklzxcvbnm','QWERTYUIOPASDFGHJKLZXCVBNM')"/>
     <xsl:apply-templates select="uri[contains('Yy',@partial)]" mode="mirror"/>
   </xsl:for-each>
  </xsl:when>
 </xsl:choose>
</xsl:template>

<xsl:template match="uri" mode="mirror">
  <uri link="{.}">
    <xsl:variable name="ipv6-only">
     <xsl:if test="contains('nN', @ipv4) and contains('yY', @ipv6)">
      <xsl:text>/ipv6 only</xsl:text>
     </xsl:if>
    </xsl:variable>
    <xsl:choose>
    <xsl:when test="contains('yY', @partial)">
      <xsl:value-of select="concat(preceding-sibling::name, ' (', key('country', ../../@country) , '/', @protocol, $ipv6-only, ')')"/>
    </xsl:when>
    <xsl:when test="contains('nN', @partial)">
      <xsl:value-of select="concat(preceding-sibling::name, ' (', @protocol, $ipv6-only, ')')"/>
    </xsl:when>
    </xsl:choose>
    <xsl:if test="contains('yY', @ipv4) and contains('yY', @ipv6)">
     <xsl:text>*</xsl:text>
    </xsl:if>
  </uri>
  <br/>
</xsl:template>

</xsl:stylesheet>
