<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="exslt"
                version="1.0">

<xsl:include href="/xsl/job.xsl"/>

<xsl:output encoding="UTF-8" method="xml" indent="no" doctype-system="/dtd/guide.dtd"/>

<xsl:template match="/staffingNeeds">
<guide>
<xsl:apply-templates/>
</guide>
</xsl:template>


<xsl:template match="today">
  <!--<date><xsl:value-of select="exslt:node-set($devaway)/devaway/@date"/></date>-->
  <date>today</date>
</xsl:template>

<xsl:template match="jobs">
  <xsl:variable name="projects" select="document('/proj/en/index.xml')/projects"/>
  <xsl:for-each select="document($projects)/project/subproject">
    <xsl:sort select="translate(normalize-space(document(string(@ref))/project/name),'QWERTYUIOPLKJHGFDSAZXCVBNM','qwertyuioplkjhgfdsazxcvbnm')"/>
    <xsl:call-template name="a-project">
     <xsl:with-param name="prefix" select="''"/>
     <xsl:with-param name="project-page" select="@ref"/>
    </xsl:call-template>
  </xsl:for-each>
</xsl:template>

<xsl:template name="a-project">
 <xsl:param name="prefix"/>
 <xsl:param name="project-page"/>

 <xsl:variable name="project" select="document($project-page)"/>
 <xsl:if test="$project/project/recruitment">
 <chapter>
 <title>
  <xsl:value-of select="concat($prefix, $project/project/name)"/>
 </title>
 <section><body><p>
 <xsl:value-of select="$project/project/description"/><br/>(<uri link="{$project-page}">Link to project page</uri>)
 </p></body></section>
 <xsl:apply-templates select="$project/project/recruitment/job"/>
 </chapter>
 </xsl:if>

 <!-- Do subprojects -->
 <xsl:for-each select="$project/project/subproject">
  <xsl:sort select="translate(normalize-space(document(string(@ref))/project/name),'QWERTYUIOPLKJHGFDSAZXCVBNM','qwertyuioplkjhgfdsazxcvbnm')"/>
    <xsl:call-template name="a-project">
     <xsl:with-param name="prefix" select="concat($project/project/name, ' -- ')"/>
     <xsl:with-param name="project-page" select="@ref"/>
    </xsl:call-template>
 </xsl:for-each>

</xsl:template>

<xsl:template match="*|@*|text()">
  <xsl:copy>
    <xsl:apply-templates select="*|@*|text()"/>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>
