<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" version="1.0">
<xsl:template name="copyData">
  <xsl:copy>
    <xsl:copy-of select="@*"/>
    <xsl:apply-templates/>
  </xsl:copy>
</xsl:template>
<xsl:template match="*">
  <xsl:param name="statusFilter"/>
  <xsl:choose>
    <xsl:when test="name() = 'address'"/>
    <xsl:when test="name() = 'birthday'"/>
    <xsl:when test="name() = 'email'">
      <xsl:choose>
        <xsl:when test="@role != 'gentoo'"/>
        <xsl:otherwise><xsl:call-template name="copyData"/></xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:when test="name() = 'user'">
      <xsl:choose>
	<xsl:when test="$statusFilter = ''">
          <xsl:if test="count(status) = 0"><xsl:call-template name="copyData"/></xsl:if>
	</xsl:when>
	<xsl:otherwise>
          <xsl:if test="status = $statusFilter"><xsl:call-template name="copyData"/></xsl:if>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:when test="name() = 'phonenumber'"/>
    <xsl:otherwise><xsl:call-template name="copyData"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>
</xsl:stylesheet>
