<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns="http://purl.org/rss/1.0/">

  <xsl:output
    encoding="UTF-8"
    method="xml"
    indent="yes"/>

  <xsl:template match="/glsaindex-rdf">
    <xsl:variable name="src" select="'/dyn/glsa-index.xml'"/>
<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns="http://purl.org/rss/1.0/">

<channel rdf:about="http://www.gentoo.org/security/en/index.xml">
  <title>Gentoo Linux Security Advisories</title>
  <link>http://www.gentoo.org/security/en/index.xml</link>
  <description>
    This index is automatically generated from XML source. Please contact the
    Gentoo Linux Security Team (security@gentoo.org) for related inquiries.
  </description>
  <items>
    <rdf:Seq>
    <xsl:for-each select="document($src)/guide/chapter[1]/section[1]/body/table[1]/tr[position()&gt;1]">
      <rdf:li>
        <xsl:attribute name="rdf:resource"><xsl:value-of select="ti[1]/uri/@link"/></xsl:attribute>
      </rdf:li>
    </xsl:for-each>
    </rdf:Seq>
  </items>
</channel>

<xsl:for-each select="document($src)/guide/chapter[1]/section[1]/body/table[1]/tr[position()&gt;1]">
<item>
  <xsl:variable name="glsalink" select="ti[1]/uri/@link"/>
  <xsl:attribute name="rdf:about"><xsl:value-of select="$glsalink"/></xsl:attribute>
  <title><xsl:value-of select="concat('GLSA ', normalize-space(ti[1]/uri/text()), ': ', substring-before(normalize-space(ti[2]/text()), ' '), '...')"/></title>
  <link><xsl:value-of select="$glsalink"/></link>
  <description>
    <xsl:value-of select="normalize-space(ti[2]/text())"/>
  </description>
</item>
</xsl:for-each>

</rdf:RDF>
</xsl:template>

</xsl:stylesheet>
