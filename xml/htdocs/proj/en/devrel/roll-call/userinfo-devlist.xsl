<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mainpage SYSTEM "/dtd/guide.dtd">
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:preserve-space elements="*"/>
<xsl:param name="statusFilter"/>

<xsl:template match="/userlist">
  <mainpage id="about">
    <title>Gentoo Linux Developers</title>
    <author title="Script"><mail link="devrel@gentoo.org">Gentoo Developer Relations</mail></author>
    
    <version>Current</version>
    <chapter>
      <section>
	<title>
	  Gentoo Linux
	  <xsl:choose>
	    <xsl:when test="$statusFilter = ''">Active</xsl:when>
	    <xsl:when test="$statusFilter = 'Retired'">Former</xsl:when>
	    <xsl:otherwise>'<xsl:value-of select="$statusFilter"/>'</xsl:otherwise>
	  </xsl:choose>
	  Developer List
	</title>
	<body>
	  <p>
	    <xsl:choose>
	      <xsl:when test="$statusFilter = ''">
	        The following table contains a list of active Gentoo developers. Inactive
	        developers are listed at the <uri link="/proj/en/devrel/roll-call/inactive-devs.xml">Gentoo
                Developer Relations Inactive Developers</uri> page and retired developers are listed on the <uri 
                link="/proj/en/devrel/roll-call/userinfo.xml?statusFilter=Retired">Gentoo Developer Relations Former
		Developers</uri> page.
	      </xsl:when>
	      <xsl:when test="$statusFilter = 'Retired'">
		The following table contains a list of former Gentoo developers. Active developers are listed
		on the <uri link="/proj/en/devrel/roll-call/userinfo.xml">Gentoo Linux Developer List</uri> and
		inactive developers are listed at the <uri link="/proj/en/devrel/roll-call/inactive-devs.xml">Gentoo
		Developer Relations Inactive Developers</uri> page.
	      </xsl:when>
	    </xsl:choose>
	  </p>
	  <xsl:if test="$statusFilter = ''">
            <p>
              Developers can be reached by sending e-mail to the
              developer's user name at gentoo.org; and many developers
              may be found on IRC (freenode) in #gentoo or #gentoo-dev
              (requires voicing to speak) using their user name as their
              IRC nick.
            </p>
	  </xsl:if>
	  <table>
	    <tr>
	      <th>Username</th>
	      <th>Name</th>
	      <xsl:if test="$statusFilter != 'Retired'">
		<th>GPG key</th>
	      </xsl:if>
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
		<xsl:if test="$statusFilter != 'Retired'">
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
		</xsl:if>
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
