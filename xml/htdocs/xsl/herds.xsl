<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output encoding="iso-8859-1" method="xml" indent="yes"/>

<xsl:template match="/herds">
	<xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/xsl/guide.xsl"</xsl:processing-instruction>
	<guide  link="index.xml" type="project">
		<title>Herds</title>
		<author title="script generated">Gentoo Project</author>
		<abstract>This is a list of the package maintenance groups under the Gentoo project, and who maintain those packages.</abstract>
		<version>1.0.1</version>
		<date>automatically</date>
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
	</guide>
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
	<section>
	<title>Maintainers</title>
	<body>
	<ul><xsl:apply-templates select="maintainer"><xsl:sort select="email"/></xsl:apply-templates></ul>
	</body>
	</section>
	</chapter>
</xsl:template>

<xsl:template match="description">
	<xsl:value-of select="."/>
</xsl:template>

<xsl:template match="maintainer">
	<li>
	<xsl:apply-templates select="email"/>
	<xsl:apply-templates select="name"/>
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
