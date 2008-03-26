<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="job">
  <section>
   <title><xsl:value-of select="summary"/></title>
   <body>
   <dl>
    <xsl:if test="details/text() or details/*">
      <dt>Job description</dt>
      <dd><xsl:apply-templates select='details'/></dd>
    </xsl:if>

    <xsl:if test="requirements/text() or requirements/*">
      <dt>Requirements</dt>
      <dd><xsl:apply-templates select='requirements'/></dd>
    </xsl:if>

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

<xsl:template match="requirements//node()|requirements//@*|details//node()|details//@*">
  <xsl:copy>
    <xsl:apply-templates select="node()|@*"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="job" mode="table">
  <xsl:param name="rows" select="count($project/project/recruitment/job)"/>
  <xsl:param name="link" select="$project-page"/>
  <xsl:param name="name" select="concat($prefix, $project/project/name)"/>

  <tr>
   <xsl:if test="position()=1"><ti rowspan="{$rows}}"><uri link="{$link}"><xsl:value-of select="$name"/></uri></ti></xsl:if>
   <ti><xsl:value-of select="summary"/></ti>
   <ti><xsl:apply-templates select='details'/></ti>
   <ti><xsl:apply-templates select='requirements'/></ti>
   <ti>
     <xsl:for-each select="contact">
      <xsl:if test="position()>1">, </xsl:if>
      <mail><xsl:value-of select="."/></mail>
     </xsl:for-each>
    </ti>
  </tr>
</xsl:template>
</xsl:stylesheet>
