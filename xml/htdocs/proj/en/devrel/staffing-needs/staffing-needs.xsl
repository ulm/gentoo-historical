<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:exslt="http://exslt.org/common"
                xmlns:func="http://exslt.org/functions"
                extension-element-prefixes="exslt func"
                version="1.0">

<xsl:output encoding="UTF-8" method="xml" indent="no" doctype-system="/dtd/project.dtd"/>
<xsl:include href="/xsl/inserts.xsl"/>

<xsl:template match="/staffingNeeds">
<project>
  <name>Staffing Needs</name>
  <longname>Gentoo Linux Staffing Needs</longname>

  <date>today</date>
  <author title="Script"><mail link="devrel@gentoo.org">Gentoo Developer Relations</mail></author>

  <description>
    This page lists requests for Gentoo Developers the Gentoo Recruiters have received.
  </description>
  <longdescription>
    This page aims to list the areas in which Gentoo actively seeks to
    expand development efforts. Positions are open to both existing
    Gentoo developers and also those wishing to become a Gentoo
    developer. The priorities shown are sorted from highest to lowest.
  </longdescription>
  <extrachapter position="bottom">
    <title>Gentoo Linux Staffing Needs</title>
    <section>
    <body>
      <p>
        This page does not list the only areas where contributions are
        welcome, but is only a reflection of where developers are
        needed the most. If you are interested in helping out in
        another area, then do not hesitate to contact the relevant
        development group anyway.
      </p>
      <p>
        If you are interested in helping the Gentoo Documentation
        Project, then please see
        the <uri link="/proj/en/gdp/roadmap.xml">GDP Roadmap</uri> for
        bugs that require attention.
      </p>
      <p>
        If you are interested in helping out with any of the following tasks,
        please contact the <mail link="recruiters@gentoo.org">Gentoo Recruiters</mail>,
        CCing the displayed "Contact" on your application.
      </p>
      <table>
        <tr>
          <th>Priority</th>
          <th>Summary</th>
          <th>Description</th>
        </tr>
        <xsl:for-each select="needed">
          <!-- Key by priority; then alphabetically...
         No @priority is treated lowest, so this works as we need it to. -->
          <xsl:sort select="summary/@priority" order="ascending"/>
          <!-- Yes, this is messy; but XSLT doesn't natively
         support case-insensitive sorting. This does it. -->
          <xsl:sort select="translate(summary, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
          <tr>
            <ti>
              <xsl:choose>
                <xsl:when test="summary/@priority != ''">
                  <xsl:value-of select="summary/@priority"/>
                </xsl:when>
                <xsl:otherwise>1</xsl:otherwise>
              </xsl:choose>
            </ti>
            <ti>
              <xsl:value-of select="summary"/>
            </ti>
            <ti>
              Requested on
              <xsl:value-of select="func:format-date(summary/@dateRequested,'en')"/> by
              <xsl:choose>
                <xsl:when test="contact/@herd != ''">the </xsl:when>
                <xsl:when test="contact/@team != ''">the </xsl:when>
              </xsl:choose>
              <xsl:choose>
                <xsl:when test="contact/@name != ''">
                  <mail link="{contact}">
              <xsl:value-of select="contact/@name"/>
              <xsl:choose>
                <!-- IMPORTANT: Do not split up the two
                     lines below -->
                <xsl:when test="contact/@herd != ''"> Herd</xsl:when>
                <xsl:when test="contact/@team != ''"> Team</xsl:when>
              </xsl:choose>
                  </mail>:
                </xsl:when>
                <xsl:otherwise>
                  <mail link="{contact}">
              <xsl:value-of select="contact"/>
              <xsl:choose>
                <!-- IMPORTANT: Do not split up the two
                     lines below -->
                <xsl:when test="contact/@herd != ''"> Herd</xsl:when>
                <xsl:when test="contact/@team != ''"> Team</xsl:when>
              </xsl:choose>
                  </mail>:
                </xsl:otherwise>
              </xsl:choose>
              <xsl:text> </xsl:text>
              <xsl:value-of select="description"/>
            </ti>
          </tr>
        </xsl:for-each>
      </table>
    </body>
    </section>
  </extrachapter>
</project>
</xsl:template>
</xsl:stylesheet>
