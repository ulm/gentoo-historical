<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output encoding="iso-8859-1" method="xml" indent="yes"/>

<xsl:template match="/herds">
	<xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/xsl/guide.xsl"</xsl:processing-instruction>
	<mainpage id="herds">
		<title>Herds</title>
		<author title="script">herds.xsl</author>
		<version>1.0.0</version>
		<chapter>
			<title>Herds List</title>
			<section>
			<body>
			<dl>
			<xsl:apply-templates>
				<xsl:sort select="name"/>
			</xsl:apply-templates>
			</dl>
			</body>
			</section>
		</chapter>
	</mainpage>
</xsl:template>

<xsl:template match="herd">
	<dt><b><xsl:value-of select="name"/></b></dt><br/>
	<dd>
	<xsl:apply-templates select="description"/><p/>
	Maintainers:<br/>
	<ul><xsl:apply-templates select="maintainer"><xsl:sort select="email"/></xsl:apply-templates></ul>
	</dd>
	<p/>
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
