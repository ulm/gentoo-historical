<?xml version="1.0" encoding="iso-8859-1"?>
<!-- Identity xsl transformation to allow downloading of other documents
  without the automatic translation kicking in -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output encoding="UTF-8" method="xml" indent="yes"/>
<xsl:template match="/project">
<xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/xsl/guide.xsl"</xsl:processing-instruction>
        <guide  link="index.xml" type="project">
                <title><xsl:apply-templates select="name"/></title>
		<author title="script generated">Gentoo Project</author>
		<abstract><xsl:apply-templates select="description"/></abstract>
		<version>1.0</version>
		<date>20 Sept 2003</date>
		<chapter>
			<title>Project Description</title>
			<section><body>
			<xsl:apply-templates select="longdescription"/>
			</body></section>
		</chapter>
		<xsl:apply-templates select='extrachapter[@position="top"]'/>
		<!-- here extra chapters would appear-->
		<xsl:if test="goals">
		<chapter>
			<title>Project goals</title>
			<section><body>
			<xsl:apply-templates select="goals"/>
			</body></section>
		</chapter>
		</xsl:if>
		<xsl:if test="dev">
		<chapter>
			<title>Developers</title>
			<section><body>
			<table><tr>
				 <th>Developer</th>
				 <th>Nickname</th>
				 <th>Role</th>
			       </tr>
			       <xsl:apply-templates select='dev[@role="lead"]'/>
			       <xsl:apply-templates select='dev[@role and not(@role="lead")]'>
			       	<xsl:sort select="@role"/>
			       	<xsl:sort select="text()"/>
			       </xsl:apply-templates>
			       <xsl:apply-templates select='dev[not(@role)]'/>
			</table></body></section>
		</chapter>
		</xsl:if>
		<xsl:if test="resource">
		<chapter>
			<title>Resources</title>
			<section><body>
			<p>Resources offered by the
			<xsl:value-of select="normalize-space(/project/name/text())"/>
			project are:</p>
			<ul>
			<xsl:apply-templates select="resource"/>
			</ul>
			</body></section>
		</chapter>			
		</xsl:if>
		<xsl:if test="subproject|extraproject">
		<chapter>
			<title>Subprojects</title>
			<section><body>
			<p>The <xsl:value-of select="normalize-space(/project/name/text())"/>
			project has the following subprojects:
			</p>
			<table><tr>
				 <th>Project</th>
				 <th>Lead</th>
				 <th>Description</th>
			       </tr>
			       <xsl:apply-templates select="subproject|extraproject">
				   <xsl:with-param name="ref" select="@ref"/>			       
			       </xsl:apply-templates>
			</table></body></section>
		</chapter>
		</xsl:if>		
		<xsl:apply-templates select='extrachapter[@position="subproject"]'/>
		<xsl:if test="herd">
		<chapter>
			<title>Herds</title>
			<section><body>
			<p>The <xsl:value-of select="normalize-space(/project/name/text())"/>
			project maintains the following herds:
			</p>
			<table><tr>
				 <th>Herd</th>
				 <th>Members</th>
				 <th>Description</th>
			       </tr>
			       <xsl:apply-templates select="herd">
			       </xsl:apply-templates>
			</table></body></section>
		</chapter>
		</xsl:if>		
	

		<xsl:apply-templates select='extrachapter[@position="bottom"]|extrachapter[@position=""]'/>
	</guide>
</xsl:template>
<xsl:template match="name|description">
<xsl:value-of select="normalize-space(text())"/>
</xsl:template>
<xsl:template match="longdescription|goals">
	<xsl:apply-templates select="node()|@*" />
</xsl:template>
<xsl:template match="longdescription//node()|longdescription//@*|goals//node()|goals//@*|extrachapter//node()|extrachapter//@*|extraproject//node()|extraproject//@*">
	<xsl:copy>
		<xsl:apply-templates select="node()|@*"/>
	</xsl:copy>
</xsl:template>
<xsl:template match="dev">
<xsl:variable name="nick" select='string(text())'/>
	<tr>
		<ti>
			<xsl:call-template name="fullname">
				<xsl:with-param name="nick" select="$nick"></xsl:with-param>
			</xsl:call-template>
		
		</ti>
		<ti>
			<xsl:value-of select="$nick"/>
		</ti>
		<ti>
			<xsl:value-of select="@role"/>
			<xsl:if test="@description">
				<xsl:text> ( </xsl:text>
				<xsl:value-of select="@description"/>
				<xsl:text> )</xsl:text>
			</xsl:if>
		</ti>
	</tr>
</xsl:template>
<xsl:template name="fullname">
<xsl:param name="nick" select=""/>
<xsl:param name="fallback" select="false"/>
<xsl:if test='not($nick="")'>
<xsl:choose>
<xsl:when test='document("/proj/en/metastructure/userinfo.xml")//user[@username=$nick]'>
<xsl:apply-templates select='document("/proj/en/metastructure/userinfo.xml")//user[@username=$nick]'/>
</xsl:when>
<xsl:otherwise>
<xsl:if test='$fallback="true"'>
<xsl:value-of select="$nick"/>
</xsl:if>
</xsl:otherwise>
</xsl:choose>
</xsl:if>
</xsl:template>

<xsl:template match="userlist/user">
	<xsl:value-of select="realname/firstname/text()"/>
	<xsl:text> </xsl:text>
	<xsl:value-of select="realname/familyname/text()"/>
</xsl:template>
<xsl:template match="extraproject">
	<tr><ti><xsl:value-of select="@name"/></ti>
	<ti><xsl:if test="@lead">
		<xsl:call-template name="fullname">
			<xsl:with-param name="nick"><xsl:value-of select="@lead"/></xsl:with-param>
			<xsl:with-param name="fallback">true</xsl:with-param>
		</xsl:call-template>
	</xsl:if></ti>
	<ti><xsl:apply-templates select="node()"/>
	</ti></tr>
</xsl:template>
<xsl:template match="subproject">
	<xsl:variable name="ref" select='string(@ref)'/>
	<xsl:for-each select='document($ref)'>
		<tr><ti>
		<uri link="{$ref}">
			<xsl:value-of select="/project/name/text()"/>
		</uri>
		</ti>
		<ti>
		<xsl:if test='/project/dev[@role="lead"]'>
			<xsl:call-template name="fullname">
				<xsl:with-param name="nick"><xsl:value-of select='/project/dev[@role="lead"]'/></xsl:with-param>
				<xsl:with-param name="fallback">true</xsl:with-param>
			</xsl:call-template>
		</xsl:if>
		</ti>
		<ti><xsl:value-of select="normalize-space(/project/description/text())"/></ti>
		</tr>
	</xsl:for-each>
</xsl:template>
<xsl:template match="resource">
<li><uri><xsl:attribute name="link"><xsl:value-of select="@link"/>
</xsl:attribute>
<xsl:value-of select="text()"/>
</uri>
</li>
</xsl:template>
<xsl:template match="extrachapter">
<chapter>
<xsl:apply-templates/>
</chapter>
</xsl:template>

<xsl:template match="herd">
  <xsl:for-each select='document("/proj/en/metastructure/herds/herds.xml")/herds/herd[name/text()=current()/@name]'>
    <tr>
      <ti>
        <uri>
	  <xsl:attribute name="link">
	    /proj/en/metastructure/herds/herds.xml?select=<xsl:value-of select="name"/>
	  </xsl:attribute>
	  <xsl:value-of select="name"/>
	</uri>
      </ti>
      <ti>
	<xsl:for-each select="maintainer/email">
	  <xsl:sort/>
	  <xsl:value-of select='substring-before(text(),"@gentoo.org")'/>
	  <xsl:if test="not(position()=last())">
	    <xsl:text>, </xsl:text>
	  </xsl:if>
	</xsl:for-each>
      </ti>
      <ti>
	<xsl:value-of select="description"/>
      </ti>
    </tr>
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
