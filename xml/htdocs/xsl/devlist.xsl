<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                xmlns="http://earth.google.com/kml/2.1"
                extension-element-prefixes="exslt">
<xsl:output omit-xml-declaration="yes" indent="yes" cdata-section-elements="description"/>

<xsl:param name="mode"/>

<xsl:variable name="rollcall" xmlns="">
 <xsl:for-each select="document('userinfo.xml', .)/userlist/user">
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
   <roles><xsl:value-of select="normalize-space(roles)"/></roles>
   </user>
  </xsl:if>
 </xsl:for-each>
</xsl:variable>

<xsl:template match="/">
  <xsl:choose>
    <xsl:when test="$mode='yaml'">
      <xsl:apply-templates mode="yaml"/>
    </xsl:when>
    <xsl:when test="$mode='kml'">
      <xsl:apply-templates mode="kml"/>
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
 <xsl:variable name="single-quote">'</xsl:variable>
 <xsl:variable name="double-quote">"</xsl:variable>
 <xsl:variable name="roles" select="translate(roles, $double-quote, $single-quote)"/>
 <xsl:value-of select="concat('    {&#34;nick&#34;: &#34;', @nick,'&#34;, &#34;name&#34;: &#34;', name, '&#34;, &#34;lat&#34;: ', location/@lat, ', &#34;lon&#34;: ', location/@lon, ', &#34;roles&#34;: &#34;', $roles, '&#34;}')"/>
 <xsl:if test="position()!=last()">,</xsl:if>
 <xsl:text>&#xA;</xsl:text>
</xsl:template>


<!-- kml for google earth -->
<xsl:template match="/devlist" mode="kml">
<xsl:text disable-output-escaping="yes">&lt;?xml version="1.0" encoding="UTF-8"?&gt;&#xA;</xsl:text>
<kml>
<Document>
  <xsl:apply-templates select="exslt:node-set($rollcall)/user" mode="kml"/>
</Document>
</kml>
</xsl:template>

<xsl:template match="user" mode="kml">
   <Placemark>
    <name><xsl:value-of select="@nick"/></name>
    <description>
        &lt;b&gt;<xsl:value-of select="name"/>&lt;/b&gt;&lt;br/&gt;
        &lt;i&gt;<xsl:value-of select="roles"/>&lt;/i&gt;
    </description>
    <Point>
      <coordinates><xsl:value-of select="concat(location/@lon, ',', location/@lat)"/></coordinates>
    </Point>
  </Placemark>
</xsl:template>

</xsl:stylesheet>
