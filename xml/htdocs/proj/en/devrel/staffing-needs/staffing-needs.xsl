<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mainpage SYSTEM "/dtd/guide.dtd">
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" version="1.0">
<xsl:strip-space elements="*"/>

<xsl:template match="/staffingNeeds">
  <mainpage id="about">
    <title>Gentoo Linux Staffing Needs</title>
    <author title="Script"><mail link="devrel@gentoo.org">Gentoo Developer Relations</mail></author>

    <version>Current</version>
    <chapter>
      <section>
	<title>Gentoo Linux Staffing Needs</title>
	<body>
	  <p>
	    The following table contains a list of open vacancies for
	    both existing Gentoo developers and those wishing to
	    become a Gentoo developer.
	  </p>
	  <p>
	    If you are interested in helping out with any of the
	    following tasks, then please contact the
	    <mail link="recruiters@gentoo.org">Gentoo
	    Recruiters</mail>, CCing the displayed "Contact" on your
	    application.
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
	      <xsl:sort select="summary/@priority" order="descending"/>
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
		  Requested at
		  <xsl:value-of select="summary/@dateRequested"/> by
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
    </chapter>
  </mainpage>
</xsl:template>
</xsl:stylesheet>
