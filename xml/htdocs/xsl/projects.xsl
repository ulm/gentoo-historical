<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output encoding="UTF-8" method="xml" indent="yes"/>
<xsl:param name="showlevel">2</xsl:param>
<xsl:template match="/projects">
<xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/xsl/guide.xsl"</xsl:processing-instruction>
        <guide  link="index.xml" type="project">
                <title>Project Listing</title>
		<author title="script generated">Gentoo Project</author>
		<abstract>This is an overview of all current gentoo projects</abstract>
		<version>1.0</version>
		<date>20 Sept 2003</date>
		<chapter>
			<title>Gentoo Projects</title>
			<section><body>
			<p>This page is meant to give an overview of all gentoo projects</p>
			<p>The old, static, version of the document is available <uri link="oldprojects.xml">here</uri></p>
			</body></section>
		</chapter>
		<chapter>
			<title>Project listing</title>
			<section><body>
			<p>
			  <xsl:choose>
			    <xsl:when test="$showlevel&lt;=1">
			      <uri link="projects.xml?showlevel=2">
			        Show sub-projects
			      </uri>
			    </xsl:when>
			    <xsl:otherwise>
			      <uri link="projects.xml?showlevel=1">
			        Hide sub-projects
			      </uri>
			    </xsl:otherwise>
			  </xsl:choose>
			</p>
			<table>
			  <xsl:if test="$showlevel&lt;=1">
			    <tr>
			      <th>toplevel</th>
			      <th>lead</th>
			      <th>members</th>
			      <th>description</th>
			    </tr>
			  </xsl:if>
			  <xsl:call-template name="projlist">
			    <xsl:with-param name="ref" select="string(text())"/>
			    <xsl:with-param name="level" select="0"/>
			  </xsl:call-template>
			</table>
			</body></section>
		</chapter>
	</guide>
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

<xsl:template name="projlist">
  <xsl:param name="ref" select=""/>
  <xsl:param name="level" select="1"/>
  <xsl:if test='(number($level)=1) and ($showlevel>1)'>
    <tr>
      <th>toplevel</th>
      <xsl:if test="$showlevel>1"><th>project</th></xsl:if>
      <xsl:if test="$showlevel>2"><th>subproject</th></xsl:if>
      <th>lead</th>
      <th>members</th>
      <th>description</th>
    </tr>
  </xsl:if>
  <xsl:for-each select="document($ref)">
    <xsl:if test="($level > 0) and ($level &lt;=$showlevel)">
      <tr>
        <ti>
       	  <xsl:if test="$level=1">
       	    <uri>
       	      <xsl:attribute name="link">
       	        <xsl:value-of select="$ref"/>
       	      </xsl:attribute>
      	      <xsl:value-of select="project/name/text()"/>
      	    </uri>
          </xsl:if>
        </ti>
        <xsl:if test="$showlevel>1">
          <ti>
      	    <xsl:if test="$level=2">
              <uri>
       	        <xsl:attribute name="link">
       	          <xsl:value-of select="$ref"/>
                </xsl:attribute>
      	        <xsl:value-of select="project/name/text()"/>
      	      </uri>
      	    </xsl:if>
          </ti>
        </xsl:if>
        <xsl:if test="$showlevel>2">
          <ti>
      	    <xsl:if test="$level=3">
       	      <uri>
       	        <xsl:attribute name="link">
                  <xsl:value-of select="$ref"/>
                </xsl:attribute>
                <xsl:value-of select="project/name/text()"/>
              </uri>
            </xsl:if>
          </ti>
        </xsl:if>
        <ti>
          <xsl:value-of select='project/dev[@role="lead"]'/>
        </ti>
        <ti>
          <xsl:for-each select="project/dev[not(@role='lead')]">
            <xsl:sort select="text()"/>
            <xsl:value-of select="text()"/>
            <xsl:if test="not(position()=last())">
            <xsl:text>, </xsl:text>
            </xsl:if>
          </xsl:for-each>
        </ti>
        <ti>
          <xsl:apply-templates select="project/description"/>
        </ti>
      </tr>
    </xsl:if>
    <xsl:for-each select="project/subproject">
      <xsl:sort select="document(@ref)/project/name"/>
      <xsl:call-template name="projlist">
        <xsl:with-param name="ref" select="string(@ref)"/>
        <xsl:with-param name="level" select="$level + 1"/>
      </xsl:call-template>
    </xsl:for-each>
    <xsl:for-each select="project/extraproject">
      <xsl:sort select="@name"/>
      <xsl:call-template name="extraproj">
        <xsl:with-param name="level" select="$level + 1"/>
      </xsl:call-template>
    </xsl:for-each>
  </xsl:for-each>
</xsl:template>

<xsl:template match="/project/description//node()|project/description//@*|/project/extraproject//@*|/project/extraproject//node()">
  <xsl:copy>
    <xsl:apply-templates select="node()|@*"/>
  </xsl:copy>
</xsl:template>

<xsl:template name="extraproj">
  <xsl:param name="level" select="1"/>
  <xsl:if test='(number($level)=1) and ($showlevel>1)'>
    <tr>
      <th>toplevel</th>
      <xsl:if test="$showlevel>1"><th>project</th></xsl:if>
      <xsl:if test="$showlevel>2"><th>subproject</th></xsl:if>
      <th>lead</th>
      <th>members</th>
      <th>description</th>
    </tr>
  </xsl:if>
  <xsl:if test="($level > 0) and ($level &lt;=$showlevel)">
    <tr>
      <ti>
        <xsl:if test="$level=1">
          <xsl:value-of select="@name"/>
        </xsl:if>
      </ti>
      <xsl:if test="$showlevel>1">
      <ti>
        <xsl:if test="$level=2">
          <xsl:value-of select="@name"/>
      	</xsl:if>
      </ti>
      </xsl:if>
      <xsl:if test="$showlevel>2">
      <ti>
        <xsl:if test="$level=3">
    	  <xsl:value-of select="@name"/>
        </xsl:if>
      </ti>
      </xsl:if>
      <ti>
        <xsl:value-of select='@lead'/>
      </ti>
      <ti>
      </ti>
      <ti>
        <xsl:apply-templates select="node()"/>
      </ti>
    </tr>
  </xsl:if>
</xsl:template>


</xsl:stylesheet>
