<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="fullname">
  <xsl:param name="nick" select="none"/>
  <xsl:param name="fallback" select="false"/>
  <xsl:param name="parent" select="false"/>
  <xsl:if test='not($nick="none")'>
    <xsl:variable name="user" select='document("/proj/en/devrel/roll-call/userinfo.xml")//user[@username=translate($nick, "ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")]'/>
    <xsl:choose>
      <xsl:when test='$user'>
        <xsl:for-each select='$user'>
          <xsl:if test='$parent="true"'><xsl:text>(</xsl:text></xsl:if>
	    <xsl:choose>
	      <xsl:when test="realname/@fullname">
	        <xsl:value-of select="realname/@fullname"/>
	      </xsl:when>
	      <xsl:otherwise>
                <xsl:value-of select="realname/firstname/text()"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="realname/familyname/text()"/>
	      </xsl:otherwise>
	    </xsl:choose>
          <xsl:if test='$parent="true"'><xsl:text>)</xsl:text></xsl:if>
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test='$fallback="true"'>
          <xsl:if test='$parent="true"'><xsl:text>(</xsl:text></xsl:if>
          <xsl:value-of select="$nick"/>
          <xsl:if test='$parent="true"'><xsl:text>)</xsl:text></xsl:if>
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>
