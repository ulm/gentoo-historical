<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="job">
  <section>
   <title><xsl:value-of select="summary"/></title>
   <body>
   <dl>
    <dt>Job description</dt>
    <dd><xsl:apply-templates select='details'/></dd>

    <dt>Requirements</dt>
    <dd><xsl:apply-templates select='requirements'/></dd>

    <dt>Contact<xsl:if test="count(contact)>1">s</xsl:if></dt>
    <dd>
     <xsl:for-each select="contact">
      <xsl:if test="position()>1">, </xsl:if>
      <mail><xsl:value-of select="."/></mail>
     </xsl:for-each>
    </dd>
   </dl>
   </body>
  </section>
</xsl:template>
</xsl:stylesheet>
