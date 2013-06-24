<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="exslt"
                version="1.0">

<xsl:include href="/xsl/job.xsl"/>

<xsl:output encoding="UTF-8" method="xml" indent="no" doctype-system="/dtd/guide.dtd"/>

<xsl:template match="/staffingNeeds">
<guide disclaimer="obsolete" redirect="http://wiki.gentoo.org/wiki/Project:Gentoo/Staffing_Needs">
<xsl:apply-templates/>
</guide>
</xsl:template>


<xsl:template match="today">
  <!--<date><xsl:value-of select="exslt:node-set($devaway)/devaway/@date"/></date>-->
  <date>today</date>
</xsl:template>

<xsl:template match="jobs">
  <xsl:variable name="projects" select="document('/proj/en/index.xml')/projects"/>
  <chapter><title>Calls for recruitment</title><section><body><table>
  <tr>
  <th>Project</th>
  <th>Job</th>
  <th>Description</th>
  <th>Requirements</th>
  <th>Contacts</th>
  </tr>
  <xsl:for-each select="document($projects)/project/subproject">
    <xsl:sort select="translate(normalize-space(document(string(@ref))/project/name),'QWERTYUIOPLKJHGFDSAZXCVBNM','qwertyuioplkjhgfdsazxcvbnm')"/>
    <xsl:call-template name="a-project">
     <xsl:with-param name="prefix" select="''"/>
     <xsl:with-param name="project-page" select="@ref"/>
    </xsl:call-template>
  </xsl:for-each>
  </table></body></section></chapter>
</xsl:template>

<xsl:template name="a-project">
 <xsl:param name="prefix"/>
 <xsl:param name="project-page"/>

 <xsl:variable name="project" select="document($project-page)"/>
 <xsl:if test="$project/project/recruitment">
 <xsl:apply-templates select="$project/project/recruitment/job" mode="table">
  <xsl:with-param name="rows" select="count($project/project/recruitment/job)"/>
  <xsl:with-param name="link" select="$project-page"/>
  <xsl:with-param name="name" select="concat($prefix, $project/project/name)"/>
 </xsl:apply-templates>
 </xsl:if>

 <!-- Do subprojects -->
 <xsl:for-each select="$project/project/subproject">
  <xsl:sort select="translate(normalize-space(document(string(@ref))/project/name),'QWERTYUIOPLKJHGFDSAZXCVBNM','qwertyuioplkjhgfdsazxcvbnm')"/>
    <xsl:call-template name="a-project">
     <xsl:with-param name="prefix" select="concat($project/project/name, ' — ')"/>
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
