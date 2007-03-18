<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="exslt">
<xsl:output method="text" indent="no"/>

<xsl:param name="mode"/>

<xsl:variable name="rollcall">
 <xsl:for-each select="document('userinfo.xml')/userlist/user">
  <xsl:sort select="@username"/>
  <xsl:if test="translate(status,'tired', 'TIRED')!='RETIRED'">
   <user nick="{@username}">
   <name>
   <xsl:choose>
     <xsl:when test="realname/@fullname">
       <xsl:value-of select="realname/@fullname"/>
     </xsl:when>
     <xsl:otherwise>
       <xsl:value-of select="concat(realname/firstname, ' ', realname/familyname)"/>
     </xsl:otherwise>
   </xsl:choose>
   </name>
   <pgpkey><xsl:value-of select="pgpkey"/></pgpkey>
   <location>
     <xsl:if test="location/@longitude and location/@latitude">
       <xsl:attribute name="lon"><xsl:value-of select="location/@longitude"/></xsl:attribute>
       <xsl:attribute name="lat"><xsl:value-of select="location/@latitude"/></xsl:attribute>
     </xsl:if>
     <xsl:value-of select="location"/>
   </location>
   </user>
  </xsl:if>
 </xsl:for-each>
</xsl:variable>

<xsl:template match="/">
  <xsl:choose>
    <xsl:when test="$mode='yaml'">
      <xsl:apply-templates mode="yaml"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<!-- Default mode, similar to /etc/passwd -->
<xsl:template match="/devlist">
<xsl:text>#nick:name:location:latitude:longitude:pgpkey
</xsl:text>
<xsl:apply-templates select="exslt:node-set($rollcall)/user"/>
</xsl:template>

<xsl:template match="user">
 <xsl:value-of select="concat(@nick, ':', name, ':', location, ':', location/@lat, ':', location/@lon, ':', pgpkey, '&#xA;')"/>
</xsl:template>


<!-- yaml mode -->
<xsl:template match="/devlist" mode="yaml">
<xsl:text>{
  "developers": [
</xsl:text>
<xsl:apply-templates select="exslt:node-set($rollcall)/user[location/@lat]" mode="yaml"/>
<xsl:text>  ]
}
</xsl:text>
</xsl:template>

<xsl:template match="user" mode="yaml">
 <xsl:value-of select="concat('    {&#34;nick&#34;: &#34;', @nick,'&#34;, &#34;name&#34;: &#34;', name, '&#34;, &#34;lat&#34;: ', location/@lat, ', &#34;lon&#34;: ', location/@lon,'}')"/>
 <xsl:if test="position()!=last()">,</xsl:if>
 <xsl:text>&#xA;</xsl:text>
</xsl:template>


</xsl:stylesheet>
