<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mainpage SYSTEM "/dtd/guide.dtd">
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" version="1.0">
<xsl:preserve-space elements="*"/>
<xsl:template match="/userlist">
  <mainpage id="about">
    <title>Gentoo Linux Developers</title>
    <author title="Script"><mail link="devrel@gentoo.org">Gentoo Developer Relations</mail></author>
    
    <version>Current</version>
    <chapter>
      <section>
	<title>Gentoo Linux Developer List</title>
	<body>
	  <p>
	    The following table contains a list of active Gentoo developers. Retired or inactive
	    developers are listed at the <uri link="/proj/en/devrel/roll-call/inactive-devs.xml">Gentoo
            Developer Relations Inactive Developers</uri> page and the <uri 
            link="/proj/en/devrel/roll-call/alumni.xml">Developer Relations Former Developers</uri> page.
	  </p>
          <p>
            Developers can be reached by sending e-mail to the
            developer's user name at gentoo.org; and many developers
            may be found on IRC (freenode) in #gentoo or #gentoo-dev
            (requires voicing to speak) using their user name as their
            IRC nick.
          </p>
	  <table>
	    <tr>
	      <th>Username</th>
	      <th>Name</th>
              <th>GPG key</th>
              <th>Location</th>
	      <th>Areas of responsibility</th>
	    </tr>
	    <xsl:for-each select="user">
	      <xsl:sort select="@username"/>
	      <tr>
		<th><xsl:value-of select="@username"/></th>
		<ti>
		  <xsl:choose>
		    <xsl:when test="realname/@fullname">
		      <xsl:value-of select="realname/@fullname"/>
		    </xsl:when>
		    <xsl:otherwise>
		      <xsl:value-of select="realname/firstname"/><xsl:text> </xsl:text><xsl:value-of select="realname/familyname"/>
		    </xsl:otherwise>
		  </xsl:choose>
                  <xsl:if test="status">
		    <xsl:if test="status != 'active'">
		      [ <e><xsl:value-of select="concat(translate(substring(status, 1, 1 ),'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), substring(status, 2, string-length(status)))" /></e> ]
		    </xsl:if>
		  </xsl:if>
		</ti>
		<ti>
		  <xsl:choose>
		    <xsl:when test="starts-with(pgpkey, '0x')">
		      <xsl:value-of select="translate(pgpkey,'abcdef','ABCDEF')"/>
		    </xsl:when>
                    <xsl:when test="string-length(pgpkey) = 8">
		      0x<xsl:value-of select="translate(pgpkey,'abcdef','ABCDEF')"/>
		    </xsl:when>
		    <xsl:when test="string-length(pgpkey) &gt; 0">
		      Invalid key specification!
		    </xsl:when>
		    <xsl:otherwise></xsl:otherwise>
		  </xsl:choose>
		</ti>
		<ti>
		  <xsl:choose>
		    <xsl:when test="location">
		      <xsl:value-of select="location"/>
		    </xsl:when>
		    <xsl:otherwise></xsl:otherwise>
		  </xsl:choose>
		</ti>
		<ti>
		  <xsl:choose>
		    <xsl:when test="roles">
		      <xsl:value-of select="roles"/>
		    </xsl:when>
		    <xsl:otherwise></xsl:otherwise>
		  </xsl:choose>
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
