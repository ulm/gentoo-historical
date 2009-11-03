<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="exslt" >

<xsl:output encoding="UTF-8"
            method="xml"
            indent="yes"
            doctype-system="/dtd/guide.dtd"/>

<xsl:param name="statusFilter"/>

<xsl:variable name="devaway" select='document("/dyn/devaway/devaway.xml")'/>

<xsl:template match="/userlist">
  <mainpage>
    <title>Gentoo Linux Developers</title>
    <author title="Script"><mail link="devrel@gentoo.org">Gentoo Developer Relations</mail></author>

    <version>Current</version>
    <chapter>
    <title>
      Gentoo Linux
      <xsl:choose>
        <xsl:when test="$statusFilter = ''">Active</xsl:when>
        <xsl:when test="$statusFilter = 'Retired'">Former</xsl:when>
        <xsl:otherwise>'<xsl:value-of select="$statusFilter"/>'</xsl:otherwise>
      </xsl:choose>
      Developer List
    </title>
    <section>
    <body>
      <p>
        <xsl:choose>
          <xsl:when test="$statusFilter = ''">
            The following table contains a list of active Gentoo developers.
            Retired developers are listed on the <uri
            link="userinfo.xml?statusFilter=Retired">Gentoo
            Developer Relations Former Developers</uri> page.
          </xsl:when>
          <xsl:when test="$statusFilter = 'Retired'">
            The following table contains a list of former Gentoo developers.
            Active developers are listed on the <uri
            link="userinfo.xml">Gentoo Linux Developer
            List</uri>.
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
          <p>
            You might want to check the list of <uri
            link="devaway.xml">unavailable developers</uri> before trying to
            contact anyone.
          </p>
      </xsl:if>
      <table>
      <tr>
        <th>Username</th>
        <th>Name</th>
        <th>
          <xsl:if test="$statusFilter != 'Retired'">GPG key</xsl:if>
          <xsl:if test="$statusFilter = 'Retired'">Status</xsl:if>
        </th>
        <th>Location</th>
        <th>Areas of responsibility</th>
      </tr>
      <xsl:apply-templates select="user">
        <xsl:sort select="@username"/>
      </xsl:apply-templates>
    </table>
  </body>

</section>
</chapter>
</mainpage>
</xsl:template>

<xsl:template match="user">
 <xsl:if test="($statusFilter = 'Retired' and translate(status/text(),'tired','TIRED')='RETIRED') or ($statusFilter = '' and not(status))">
  <tr>
    <xsl:variable name="username" select="@username"/>
    <th><xsl:value-of select="$username"/></th>
    <ti>
      <xsl:choose>
        <xsl:when test="realname/@fullname">
          <xsl:value-of select="realname/@fullname"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="realname/firstname"/><xsl:text> </xsl:text><xsl:value-of select="realname/familyname"/>
        </xsl:otherwise>
      </xsl:choose>
    </ti>
    <ti>
      <xsl:if test="$statusFilter != 'Retired'">
       <xsl:for-each select="pgpkey">
        <xsl:choose>
          <xsl:when test="starts-with(., '0x')">
            <xsl:value-of select="translate(.,'abcdef','ABCDEF')"/>
          </xsl:when>
          <xsl:when test="string-length(.) = 8">
            0x<xsl:value-of select="translate(.,'abcdef','ABCDEF')"/>
          </xsl:when>
          <xsl:when test="string-length(.) &gt; 0">
            <xsl:text>Invalid key!</xsl:text>
          </xsl:when>
        </xsl:choose>
        <xsl:if test="not(position()=last())"><br/></xsl:if>
       </xsl:for-each>
      </xsl:if>
      <xsl:if test="$statusFilter = 'Retired'">
        <xsl:if test="status and status != 'active'">
          <xsl:value-of select="concat(translate(substring(status, 1, 1 ),'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), substring(status, 2, string-length(status)))" />
        </xsl:if>
      </xsl:if>
    </ti>
    <ti>
      <xsl:choose>
       <xsl:when test="$statusFilter != 'Retired' and location/@longitude and location/@latitude">
        <uri link="{concat('devmap.xml?dev=',@username)}"><xsl:value-of select="location"/></uri>
       </xsl:when>
       <xsl:when test="location">
        <xsl:value-of select="location"/>
       </xsl:when>
      </xsl:choose>
      <xsl:if test="$statusFilter != 'Retired' and $devaway/devaway/dev[@nick=$username]">
        (<uri><xsl:attribute name="link"><xsl:value-of select="concat('devaway.xml?select=', $username,'#',$username)"/></xsl:attribute><brite>away</brite></uri>)
      </xsl:if>
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
 </xsl:if>
</xsl:template>
</xsl:stylesheet>
