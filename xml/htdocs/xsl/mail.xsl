<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="exslt">

<!-- Process <mail> tags, in a separate .xsl to be included by both
     guide.xsl and GWN-to-text converter
  -->

<!-- Get the list of devs from the roll-call -->
<xsl:variable name="ALL-DEVS" xmlns="">
 <devs>
  <xsl:for-each select="document('/proj/en/devrel/roll-call/userinfo.xml')/userlist/user">
    <user username="{@username}">
     <xsl:if test="translate(status,'TIRED','tired')='retired'">
      <xsl:attribute name="retired"/>
     </xsl:if>
     <xsl:copy-of select="realname"/>
     <xsl:copy-of select="email"/>
    </user>
  </xsl:for-each>
 </devs>
</xsl:variable>

<!-- Process mail tag, see if we have a Gentoo dev, add @gentoo.org is required
     and pull name from roll-call if required
     Returns an xml element named mail with optional link attribute
  -->
<xsl:template name="smart-mail" xmlns="">
<xsl:param name="mail"/>

<xsl:if test="string-length($mail/@link)>0 or string-length($mail/text())>0">
 <xsl:variable name="gnick">
  <xsl:choose>
   <xsl:when test="string-length($mail/@link)=0 and not(contains($mail/text(),'@'))">
     <!-- <mail>nick</mail> -->
     <xsl:value-of select="$mail/text()"/>
   </xsl:when>
   <xsl:when test="string-length($mail/@link)=0 and contains($mail/text(),'@gentoo.org')">
     <!-- <mail>nick@gentoo.org</mail> -->
     <xsl:value-of select="substring-before($mail/text(), '@')"/>
   </xsl:when>
   <xsl:when test="string-length($mail/@link)>0 and not(contains($mail/@link,'@'))">
     <!-- <mail link="nick">blah blah</mail> -->
     <xsl:value-of select="$mail/@link"/>
   </xsl:when>
   <xsl:when test="contains($mail/@link,'@gentoo.org')">
     <!-- <mail link="nick@gentoo.org">blah blah</mail> -->
     <xsl:value-of select="substring-before($mail/@link, '@gentoo.org')"/>
   </xsl:when>
  </xsl:choose>
 </xsl:variable>

 <xsl:variable name="gmail">
  <xsl:if test="string-length($gnick)>0">
   <xsl:choose>
    <xsl:when test="exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick and @retired]">
     <xsl:value-of select="exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick]/email[substring-after(text(),'@')!='gentoo.org'][1]"/>
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick]/email[substring-after(text(),'@')='gentoo.org'][1]"/>
    </xsl:otherwise>
   </xsl:choose>
  </xsl:if>
 </xsl:variable>

 <xsl:variable name="gname">
  <xsl:if test="string-length($gnick)>0">
   <xsl:choose>
    <xsl:when test="exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick]/realname/@fullname">
     <xsl:value-of select="exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick]/realname/@fullname"/>
    </xsl:when>
    <xsl:when test="exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick]/realname[firstname or familyname]">
     <xsl:value-of select="concat(exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick]/realname/firstname,' ',exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick]/realname/familyname)"/>
    </xsl:when>
   </xsl:choose>
  </xsl:if>
 </xsl:variable>

 <xsl:variable name="href">
  <xsl:choose>
  <xsl:when test="string-length($gname)>0 and string-length($gmail)=0 and exslt:node-set($ALL-DEVS)/devs/user[@username=$gnick and @retired]"/>
    <xsl:when test="string-length($gmail)>0">
      <xsl:value-of select="$gmail"/>
    </xsl:when>
    <xsl:when test="string-length($mail/@link)>0">
      <xsl:value-of select="$mail/@link"/>
    </xsl:when>
    <xsl:when test="string-length($mail/text())>0">
      <xsl:value-of select="$mail/text()"/>
    </xsl:when>
  </xsl:choose>
 </xsl:variable>

 <xsl:variable name="content">
   <xsl:choose>
    <xsl:when test="string-length($mail/@link)>0 and string-length($mail/text())>0">
     <xsl:value-of select="$mail/text()"/>
    </xsl:when>
    <xsl:when test="string-length($gname)>0">
     <xsl:value-of select="$gname"/>
    </xsl:when>
    <xsl:when test="string-length($gmail)>0 and string-length($mail/text())=0">
     <xsl:value-of select="$gmail"/>
    </xsl:when>
    <xsl:when test="string-length($mail/text())=0">
     <xsl:value-of select="$mail/@link"/>
    </xsl:when>
    <xsl:otherwise>
     <xsl:value-of select="."/>
    </xsl:otherwise>
   </xsl:choose>
 </xsl:variable>

 <mail>
  <xsl:if test="string-length($href)>0">
   <xsl:attribute name="link">
    <xsl:value-of select="$href"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:value-of select="$content"/>
 </mail>

</xsl:if>
</xsl:template>

</xsl:stylesheet>
