<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                              xmlns:func="http://exslt.org/functions"
                                extension-element-prefixes="func"
>

<func:function name="xsl:gettext">
  <xsl:param name="str" />
  
<!-- 4DEBUGGING
<xsl:message>LANG=<xsl:value-of select="$LANG" /> || Param=<xsl:value-of select="$str" /></xsl:message>
-->
  <xsl:choose>
    <!-- Default to English version when 
           . no lang attribute is specified    or
           . when lang is not yet supported    or
           . when lang is not properly set which would make document() complain about missing file
         Default to 'UNDEFINED STRING' when 
           . requested text is not available
    -->

    <!-- Repeat the following 3 lines and define 'XX' in test against $LANG to define a new supported language
                             \  /¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                              ||                                                                               -->
    <xsl:when test="($LANG = 'fr') and (document(concat('/doc/',$LANG,'/inserts-',$LANG,'.xml'))/inserts/insert[@name=$str])">
      <func:result select="document(concat('/doc/',$LANG,'/inserts-',$LANG,'.xml'))/inserts/insert[@name=$str]" />
    </xsl:when>
    <xsl:when test="($LANG = 'it') and (document(concat('/doc/',$LANG,'/inserts-',$LANG,'.xml'))/inserts/insert[@name=$str])">
      <func:result select="document(concat('/doc/',$LANG,'/inserts-',$LANG,'.xml'))/inserts/insert[@name=$str]" />
    </xsl:when>
   <xsl:when test="document('/doc/en/inserts-en.xml')/inserts/insert[@name=$str]">
      <func:result select="document('/doc/en/inserts-en.xml')/inserts/insert[@name=$str]" />
    </xsl:when>
    <xsl:otherwise>
      <func:result select="'UNDEFINED STRING'" />
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!-- Define some globals that can be used throughout the stylesheets -->
<xsl:param name="TTOP"><xsl:value-of select="name(//*[1])" /></xsl:param> <!-- Top element name e.g. "book" -->
<xsl:param name="LANG"><xsl:value-of select="//*[1]/@lang" /></xsl:param> <!-- Value of top element's lang attribute e.g. "en" -->
<xsl:param name="LINK"><xsl:value-of select="//*[1]/@link" /></xsl:param> <!-- Value of top element's link attribute e.g. "handbook.xml" -->

<xsl:template match="/">
              <!-- 4DEBUGGING
                              <xsl:message>TTOP: <xsl:value-of select="$TTOP" /> </xsl:message>
                              <xsl:message>LANG: <xsl:value-of select="$LANG" /> </xsl:message>
                              <xsl:message>LINK: <xsl:value-of select="$LINK" /> </xsl:message>
              -->
  <xsl:apply-templates />
</xsl:template>

</xsl:stylesheet>
