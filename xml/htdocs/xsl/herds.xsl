<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output encoding="iso-8859-1" method="xml" indent="yes"/>
<xsl:param name="select" select="string('all')"/>
<xsl:include href="util.xsl"/>

<xsl:template match="/herds">
	<xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/xsl/guide.xsl"</xsl:processing-instruction>
	<guide  link="index.xml" type="project">
		<xsl:choose>
		    <xsl:when test='$select="all"'>
			<title>Herds</title>
		    </xsl:when>
		    <xsl:otherwise>
		        <title><xsl:value-of select="$select"/> herd information page</title>
		    </xsl:otherwise>
		</xsl:choose>
		<author title="script generated">Gentoo Project</author>
		<abstract>This is a list of the package maintenance groups under the Gentoo project, and who maintain those packages.</abstract>
		<version>1.0.1</version>
		<date>automatically</date>
		<xsl:choose>
		    <xsl:when test='$select="all"'>
			<chapter>
				<title>Introduction</title>
				<section>
				<body>
				<p>This is a list of the package maintenance groups under the Gentoo project, and who maintain those packages.</p>
				</body>
				</section>
			</chapter>
			<xsl:apply-templates select="herd">
				<xsl:sort select="name"/>
			</xsl:apply-templates>
		    </xsl:when>
		    <xsl:otherwise>
                      <xsl:for-each select="herd[name/text()=$select][1]">
			<chapter>
			   <title>Herd info</title>
			     <section><title>Name</title><body>
                               <xsl:value-of select="name"/>
			     </body></section>
			     <section><title>Description</title><body>
                               <xsl:value-of select="description"/>
			     </body></section>
			     <xsl:if test="email">
			       <section><title>Herd maintainers' email address</title><body>
                                 <xsl:value-of select="email"/>
			       </body></section>
			     </xsl:if>
                             <section>
                               <title>Maintainers</title>
                               <body>
                                 <ul><xsl:apply-templates select="maintainer"><xsl:sort select="email"/></xsl:apply-templates></ul>
                               </body>
                             </section>
			</chapter>
			<chapter><title>Packages primary managed by this herd</title>
			  <section>
			    <body>
			      <table><tr><th>Name</th><th>maintainer</th><th>description</th></tr>
			      <xsl:apply-templates select='document("/proj/en/metastructure/herds/pkgList.xml")/packages/pkgmetadata[herd[1]/text()=$select]'>
			        <xsl:sort select="@pkgname"/>
			      </xsl:apply-templates>
			      </table>
			    </body>
			  </section>
			</chapter>
			<xsl:if test='document("/proj/en/metastructure/herds/pkgList.xml")/packages/pkgmetadata[herd[2]/text()=$select]'>
			<chapter><title>Packages not primary managed by this herd</title>
			  <section>
			    <body>
			      <table><tr><th>Name</th><th>maintainer</th><th>description</th></tr>
			      <xsl:apply-templates select='document("/proj/en/metastructure/herds/pkgList.xml")/packages/pkgmetadata[herd[not(position()=1)]/text()=$select]'>
			        <xsl:sort select="@pkgname"/>
			      </xsl:apply-templates>
			      </table>
			    </body>
			  </section>
			</chapter>

			</xsl:if>
		     </xsl:for-each>
		  </xsl:otherwise>
		</xsl:choose>
	</guide>
</xsl:template>

<xsl:template match="pkgmetadata">
  <tr>
    <ti>
      <xsl:value-of select="@pkgname"/>
    </ti>
    <ti>
      <xsl:value-of select='substring-before(maintainer[1]/email,"@gentoo.org")'/>
      <xsl:text> </xsl:text>
	<xsl:call-template name="fullname">
	  <xsl:with-param name="nick" select='substring-before(maintainer[1]/email,"@gentoo.org")'/>
	  <xsl:with-param name="parent" select='"true"'/>
	</xsl:call-template>
    </ti>
    <ti>
      <xsl:value-of select="longdescription"/>
    </ti>
  </tr>
</xsl:template>

<xsl:template match="herd">
	<chapter>
	<title><xsl:value-of select="name"/></title>
	<section>
	<title>Description</title>
	<body>
	<p>
	<xsl:apply-templates select="description"/>
	</p>
	</body>
	</section>
	<xsl:if test="email">
		<section>
		<title>Herd maintainers' email address</title>
		<body>
		<p>
		<xsl:value-of select="email"/>
		</p>
		</body>
		</section>
	</xsl:if>
	<section>
	<title>Maintainers</title>
	<body>
	<ul><xsl:apply-templates select="maintainer"><xsl:sort select="email"/></xsl:apply-templates></ul>
	</body>
	</section>
	<section><title>Info</title><body>
	  More info on the <xsl:value-of select="name"/> herd can be found
	  <uri>
	    <xsl:attribute name="link">?select=<xsl:value-of select="name"/></xsl:attribute>
	    here
	  </uri>
	</body></section>
	</chapter>
</xsl:template>

<xsl:template match="description">
	<xsl:value-of select="."/>
</xsl:template>

<xsl:template match="maintainer">
	<li>
	<xsl:apply-templates select="email"/>
	<xsl:text> </xsl:text>
	<xsl:call-template name="fullname">
	  <xsl:with-param name="nick" select='substring-before(email,"@")'/>
	  <xsl:with-param name="parent" select='"true"'/>
	</xsl:call-template>
	<xsl:apply-templates select="role"/>
	</li>
</xsl:template>

<xsl:template match="email">
	<xsl:value-of select="."/>
</xsl:template>

<xsl:template match="name">
        <xsl:text> </xsl:text>(<xsl:value-of select="."/>)
</xsl:template>

<xsl:template match="role">
        <xsl:text> - </xsl:text><xsl:value-of select="."/>
</xsl:template>

</xsl:stylesheet>
