<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output encoding="UTF-8" method="xml" indent="no" doctype-system="/dtd/guide.dtd"/>

<xsl:template match="/amd64-tests">
<guide link="index.xml">

<title>
AMD64 test list
</title>

<author title="Gentoo/AMD64 Project">
  <mail link="amd64@gentoo.org">Gentoo/AMD64 Project</mail>
</author>
<author>
  <mail link="kugelfang@gentoo.org">Danny van Dyk</mail>
</author>

<abstract>
This document lists special test cases for the AMD64 architecture
</abstract>

<license/>

<version>1.0</version>
<date>TODAY</date>

<chapter>
<title>Guidelines</title>
<section>
<title>Disclaimer</title>
<body>

<p>
When testing hardware and/or software listed on this page, you may discover
bugs that could break your system. Please perform these tests only if you're
absolutely sure what you do!
</p>

</body>
</section>
<section>
<title>Test-Instructions</title>
<body>

<p>
Please keep in mind that when you fill a bug about any of the following
test-requests, please be as detailed as possible when you report either success
of failure of your testing efforts.  The developer that requested the test
completely relies on your judgement.
</p>

</body>
</section>
</chapter>

<chapter>
<title>Test Requests</title>
<section>
<body>

<table>
<tr>
  <th>#</th>
  <th>Developer</th>
  <th>Summary</th>
  <th>Bug #</th>
  <th>Status</th>
</tr>

<xsl:for-each select="test">
  <xsl:sort select="@status"/>
  <xsl:variable name="status">
    <xsl:choose>
    <xsl:when test="@status = 'FAILED'">
      <brite>FAILED</brite>
    </xsl:when>
    <xsl:when test="@status = 'WORKED'">
      <c>WORKED</c>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="@status"/>
    </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <tr>
  <ti>
    <xsl:value-of select="@id"/>
  </ti>
  <ti>
    <mail link="{@dev}@gentoo.org"><xsl:value-of select="@dev"/></mail>
  </ti>
  <ti>
    <xsl:value-of select="."/>
  </ti>
  <ti>
    <xsl:choose>
     <xsl:when test="1"> <!-- Test on? -->
        <xsl:value-of select="@bug"/>
     </xsl:when>
    </xsl:choose>
  </ti>
  <ti>
    <xsl:copy-of select="$status"/>
  </ti>
  </tr>
</xsl:for-each>

</table>
</body>
</section>
</chapter>
</guide>
</xsl:template>
</xsl:stylesheet>
