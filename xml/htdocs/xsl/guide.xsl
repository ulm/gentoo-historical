<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                xmlns:func="http://exslt.org/functions"
                extension-element-prefixes="exslt func" >

<xsl:output encoding="UTF-8" method="html" indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN" doctype-system="http://www.w3.org/TR/html4/loose.dtd"/>

<!-- Include external stylesheets -->
<xsl:include href="content.xsl" />
<xsl:include href="handbook.xsl" />
<xsl:include href="inserts.xsl" />

<!-- When using <pre>, whitespaces should be preserved -->
<xsl:preserve-space elements="pre"/>

<!-- Global definition of style parameter -->
<xsl:param name="style">0</xsl:param>
<xsl:param name="newsitemcount">6</xsl:param>

<!-- img tag -->
<xsl:template match="img">
  <img src="{@src}"/>
</xsl:template>

<!-- Content of /guide -->
<xsl:template name="guidecontent">
  <xsl:if test="$style != 'printable'">
    <br />
  </xsl:if>
  <h1>
    <xsl:choose>
      <xsl:when test="/guide/subtitle"><xsl:value-of select="/guide/title"/>: <xsl:value-of select="/guide/subtitle"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="/guide/title"/></xsl:otherwise>
    </xsl:choose>
  </h1>

  <xsl:choose>
    <xsl:when test="$style = 'printable'">
      <xsl:apply-templates select="author" />
      <br/>
      <i><xsl:call-template name="contentdate"/></i>
    </xsl:when>
    <xsl:otherwise>
     <xsl:if test="count(/guide/chapter)&gt;1">
      <form name="contents" action="http://www.gentoo.org">
        <b><xsl:value-of select="func:gettext('Content')"/></b>:
        <select name="url" size="1" OnChange="location.href=form.url.options[form.url.selectedIndex].value" style="font-family:sans-serif,Arial,Helvetica">
          <xsl:for-each select="chapter">
            <xsl:variable name="chapid">doc_chap<xsl:number/></xsl:variable><option value="#{$chapid}"><xsl:number/>. <xsl:value-of select="title"/></option>
          </xsl:for-each>
        </select>
      </form>
     </xsl:if>
    </xsl:otherwise>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="/guide">
      <xsl:apply-templates select="chapter"/>
    </xsl:when>
    <xsl:when test="/sections">
      <xsl:apply-templates select="/sections/section"/>
    </xsl:when>
  </xsl:choose>
  <br/>
  <xsl:if test="/guide/license">
    <xsl:apply-templates select="license" />
  </xsl:if>
  <br/>
</xsl:template>

<!-- Layout for documentation -->
<xsl:template name="doclayout">
<xsl:call-template name="commonHTMLheader" />
<title>
  <xsl:choose>
    <xsl:when test="/guide/@type='project'">Gentoo Linux Projects</xsl:when>
    <xsl:when test="/guide/@type='newsletter'">Gentoo Linux Newsletter</xsl:when>
    <xsl:when test="/sections">Gentoo Linux Handbook Page</xsl:when>
    <xsl:otherwise><xsl:value-of select="func:gettext('GLinuxDoc')"/></xsl:otherwise>
  </xsl:choose>
--
  <xsl:choose>
    <xsl:when test="subtitle"><xsl:if test="/guide/@type!='newsletter'"><xsl:value-of select="title"/>:</xsl:if> <xsl:value-of select="subtitle"/></xsl:when>
    <xsl:otherwise><xsl:value-of select="title"/></xsl:otherwise>
  </xsl:choose>
</title>

<xsl:text disable-output-escaping="yes">&lt;/head&gt;</xsl:text>
<xsl:choose>
  <xsl:when test="$style = 'printable'">
    <!-- Insert the node-specific content -->
<body bgcolor="#ffffff">
    <xsl:call-template name="content"/>
</body>
  </xsl:when>
  <xsl:otherwise>
<body style="margin:0px;" bgcolor="#ffffff">
<table width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td valign="top" height="125" bgcolor="#45347b">
    <!--
      <table cellspacing="0" cellpadding="0" border="0" width="193">
        <tr>
          <td class="logobg" valign="top" align="center" height="88">
            <a href="/"><img border="0" src="/images/gtop-s.jpg" alt="Gentoo Logo"/></a>
          </td>
        </tr>
        <tr>
          <td class="logobg" valign="top" align="center" height="36">
            <a href="/"><img border="0" src="/images/gbot-s.gif" alt="Gentoo Logo Side"/></a>
          </td>
        </tr>
      </table>
    -->
    <a href="/"><img border="0" src="/images/gtop-www.jpg" alt="Gentoo Logo"/></a>
    </td>
  </tr>
  <tr>
    <td valign="top" align="right" colspan="1" bgcolor="#ffffff">
      <table border="0" cellspacing="0" cellpadding="0" width="100%">
        <tr>
          <td width="99%" class="content" valign="top" align="left">
            <!-- Insert the node-specific content -->
            <xsl:call-template name="content"/>
          </td>
          <td width="1%" bgcolor="#dddaec" valign="top">
            <xsl:call-template name="rhcol"/>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td colspan="2" align="right" class="infohead">
      Copyright 2001-2005 Gentoo Foundation, Inc.  Questions, Comments, Corrections?  Email <a class="highlight" href="mailto:www@gentoo.org">www@gentoo.org</a>.
    </td>
  </tr>
</table>

</body>
  </xsl:otherwise>
  </xsl:choose>
<xsl:text disable-output-escaping="yes">&lt;/html&gt;</xsl:text>
</xsl:template>

<!-- Guide template -->
<xsl:template match="/guide">
<xsl:call-template name="doclayout" />
</xsl:template>

<!-- {Mainpage, News, Email} template -->
<xsl:template match="/mainpage | /news | /email">
<xsl:call-template name="commonHTMLheader" />
  <xsl:if test="/mainpage/@id='news'">
    <link rel="alternate" type="application/rss+xml" title="Gentoo Linux News RDF" href="http://www.gentoo.org/rdf/en/gentoo-news.rdf" />
  </xsl:if>
  <xsl:choose>
    <xsl:when test="/mainpage | /news">
      <title>Gentoo Linux -- <xsl:value-of select="title"/></title>
    </xsl:when>
    <xsl:when test="/email">
      <title><xsl:value-of select="subject"/></title>
    </xsl:when>
  </xsl:choose>
<xsl:text disable-output-escaping="yes">&lt;/head&gt;</xsl:text>
<body style="margin:0px;" bgcolor="#000000">

<table border="0" width="100%" cellspacing="0" cellpadding="0">
  <tr>
    <td valign="top" height="125" width="1%" bgcolor="#45347b">
    <a href="/"><img border="0" src="/images/gtop-www.jpg" alt="Gentoo Logo"/></a>
    </td>

    <td valign="bottom" align="left" bgcolor="#000000" colspan="2" lang="en">
      <p class="menu">
        <xsl:choose>
          <xsl:when test="/mainpage/@id='about'">
            <a class="highlight" href="/main/en/about.xml">About</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/main/en/about.xml">About</a>
          </xsl:otherwise>
        </xsl:choose>
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='projects'">
            <a class="highlight" href="/proj/en/index.xml?showlevel=1">Projects</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/proj/en/index.xml?showlevel=1">Projects</a>
          </xsl:otherwise>
        </xsl:choose>
        <!--
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='contract'">
            <a class="highlight" href="/main/en/philosophy.xml">Philosophy</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/main/en/philosophy.xml">Philosophy</a>
          </xsl:otherwise>
        </xsl:choose>
        -->
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='docs'">
            <a class="highlight" href="/doc/en/index.xml">Docs</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/doc/en/index.xml">Docs</a>
          </xsl:otherwise>
        </xsl:choose>
        | <a class="menulink" href="http://forums.gentoo.org">Forums</a>
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='lists'">
            <a class="highlight" href="/main/en/lists.xml">Lists</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/main/en/lists.xml">Lists</a>
          </xsl:otherwise>
        </xsl:choose>
        | <a class="menulink" href="http://bugs.gentoo.org">Bugs</a>
        | <a class="menulink" href="http://www.cafepress.com/officialgentoo/">Store</a>
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='newsletter'">
            <a class="highlight" href="/news/en/gwn/gwn.xml"> GWN</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/news/en/gwn/gwn.xml"> GWN</a>
          </xsl:otherwise>
        </xsl:choose>
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='where'">
            <a class="highlight" href="/main/en/where.xml">Get Gentoo!</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/main/en/where.xml">Get Gentoo!</a>
          </xsl:otherwise>
        </xsl:choose>
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='support'">
            <a class="highlight" href="/main/en/support.xml">Support</a> 
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/main/en/support.xml">Support</a> 
          </xsl:otherwise>
        </xsl:choose>
        |
        <xsl:choose>
          <xsl:when test="/mainpage/@id='sponsors'">
            <a class="highlight" href="/main/en/sponsors.xml">Sponsors</a>
          </xsl:when>
          <xsl:otherwise>
            <a class="menulink" href="/main/en/sponsors.xml">Sponsors</a>
          </xsl:otherwise>
        </xsl:choose>
        | <a class="menulink" href="http://planet.gentoo.org">Planet</a>
      </p>
    </td>
  </tr>
  <tr>
    <td valign="top" align="right" width="1%" bgcolor="#dddaec">
      <table width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
          <td height="1%" valign="top" align="right">
            <img src="/images/gridtest.gif" alt="Gentoo Spaceship"/>
          </td>
        </tr>
        <tr>
          <td height="99%" valign="top" align="left">
            <!--info goes here-->
            <table cellspacing="0" cellpadding="5" border="0">
              <tr>
                <td valign="top" class="leftmenu" lang="en">
                  <p class="altmenu">
                    Installation:
                    <br/>
                    <a class="altlink" href="/doc/en/handbook/index.xml">Gentoo Handbook</a>
                    <br/>
                    <a class="altlink" href="/doc/en/index.xml?catid=install#doc_chap2">Installation Docs</a>
                   <br/><br/>
                    Documentation:
                    <br/>
                    <a class="altlink" href="/doc/en/">Main Index</a>
                    <br/>
                    <a class="altlink" href="/main/en/about.xml">About Gentoo</a>
                    <br/>
                    <a class="altlink" href="/main/en/philosophy.xml">Philosophy</a>
                    <br/>
                    <a class="altlink" href="/main/en/contract.xml">Social Contract</a>
                    <br/><br/>
                    Resources:
                    <br/>
                    <a class="altlink" href="http://bugs.gentoo.org">Bug Tracker</a>
                    <br/>
                    <a class="altlink" href="http://forums.gentoo.org">Discussion Forums</a>
                    <br/>
                    <a class="altlink" href="/main/en/lists.xml">Mailing Lists</a>
                    <br/>
                    <a class="altlink" href="/main/en/irc.xml">IRC Channels</a>
                    <br/>
                    <a class="altlink" href="/security/en/index.xml">Security Announcements</a>
                    <br/>
                    <a class="altlink" href="http://packages.gentoo.org/">Online Package Database</a>
                    <br/>
                    <a class="altlink" href="/proj/en/devrel/roll-call/userinfo.xml">Developer List</a>
                    <br/>
                    <a class="altlink" href="http://viewcvs.gentoo.org/">View our CVS</a>
                    <br/>
                    <a class="altlink" href="/proj/en/devrel/staffing-needs/">Staffing Needs</a>
                    <br/>
                    <a class="altlink" href="/main/en/mirrors.xml">Mirrors</a>
                    <br/>
                    <a class="altlink" href="http://torrents.gentoo.org/">Gentoo BitTorrents</a>
                    <br/>
                    <a class="altlink" href="/proj/en/glep/">Gentoo Linux Enhancement Proposals</a>
                    <br/>
                    <a class="altlink" href="/main/en/name-logo.xml">Name and Logo Guidelines</a>
                    <!--
                    <a class="altlink" href="/dyn/index-cvs.xml">Daily CVS ChangeLog</a>
                    -->
                    <!--<a class="altlink" href="http://stats.gentoo.org">Gentoo Usage Statistics</a>
                    <br/>
                    <a class="altlink" href="http://stable.gentoo.org">Gentoo Stable Project</a>
                    <br/>
                    -->
                    <br/><br/>
                    Graphics:
                    <br/>
                    <a class="altlink" href="/main/en/graphics.xml">Logos and themes</a>
                    <br/>
                    <a class="altlink" href="/dyn/icons.xml">Icons</a>
                    <br/>
                    <a class="altlink" href="/main/en/shots.xml">ScreenShots</a>
                    <br/><br/>
                    Miscellaneous Resources:
                    <br/>
                    <a class="altlink" href="http://www.cafepress.com/officialgentoo/">Gentoo Linux Store</a>
                    <br/>
                    <a class="altlink" href="/main/en/projects.xml">Gentoo-hosted projects</a>
                    <br/>
                    <a class="altlink" href="/main/en/articles.xml">IBM dW/Intel article archive</a>
                    <xsl:if test="/mainpage/@id='news'">
                    <br/><br/>
                      Older News:<br/>
                      <xsl:for-each select="document('/dyn/news-index.xml')/uris/uri[position()&gt;$newsitemcount][position()&lt;20]/text()">
                        <xsl:variable name="newsuri" select="."/>
                        <a class="altlink" href="{$newsuri}"><xsl:value-of select="document(.)/news/title"/></a>
                        <br/>
                      </xsl:for-each>
                    </xsl:if>
                  </p>
                  <br/><br />
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
    <!-- Content below top menu and between left menu and ads -->
    <td valign="top" bgcolor="#ffffff">
            <xsl:choose>
              <xsl:when test="/mainpage/@id='news'">
              <p class="news">
                <img class="newsicon" src="/images/gentoo-new.gif" alt="Gentoo logo-"/>
                <span class="newsitem" lang="en">We produce Gentoo Linux, a special flavor of Linux that
                can be automatically optimized and customized for just
                about any application or need. Extreme performance,
                configurability and a top-notch user and developer
                community are all hallmarks of the Gentoo experience.
                To learn more, read our <b><a href="/main/en/about.xml">about
                page</a></b>.</span>
              </p>

              <xsl:for-each select="document('/dyn/news-index.xml')/uris/uri[position()&lt;=$newsitemcount]/text()">
                <div class="news">
                  <p class="newshead" lang="en">
                    <b><xsl:value-of select="document(.)/news/title"/></b>
                    <br/>
                    <font size="0.90em">
                    Posted on <xsl:value-of select="func:format-date(document(.)/news/date)"/>
                    by <xsl:value-of select="document(.)/news/poster"/>
                    </font>
                  </p>
                  <xsl:choose>
                    <xsl:when test="document(.)/news/@category='alpha'">
                      <img class="newsicon" src="/images/icon-alpha.gif" alt="AlphaServer GS160"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='kde'">
                      <img class="newsicon" src="/images/icon-kde.png" alt="KDE"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='gentoo'">
                      <img class="newsicon" src="/images/icon-gentoo.png" alt="gentoo"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='main'">
                      <img class="newsicon" src="/images/icon-stick.png" alt="stick man"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='ibm'">
                      <img class="newsicon" src="/images/icon-ibm.gif" alt="ibm"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='linux'">
                      <img class="newsicon" src="/images/icon-penguin.png" alt="tux"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='moo'">
                      <img class="newsicon" src="/images/icon-cow.png" alt="Larry the Cow"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='plans'">
                      <img class="newsicon" src="/images/icon-clock.png" alt="Clock"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='nvidia'">
                      <img class="newsicon" src="/images/icon-nvidia.png" alt="Nvidia"/>
                    </xsl:when>
                    <xsl:when test="document(.)/news/@category='freescale'">
                      <img class="newsicon" src="/images/icon-freescale.gif" alt="Freescale Semiconductor"/>
                    </xsl:when>
                  </xsl:choose>
                  
                  <div class="newsitem">
                  <xsl:choose>
                    <xsl:when test="document(.)/news/summary">
                      <xsl:apply-templates select="document(.)/news/summary"/>
                      <br/>
                      <a href="{.}"><b>(full story)</b></a>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:apply-templates select="document(.)/news/body"/>
                    </xsl:otherwise>
                  </xsl:choose>
                  </div>
                </div>
              </xsl:for-each>
              <!-- Add content after newsitems if any -->


              </xsl:when>
              <xsl:when test="/news">
                <div class="news">
                  <p class="newshead">
                    <b><xsl:value-of select="title"/></b>
                    <br/>
                    <font size="0.90em">
                    Posted on <xsl:value-of select="func:format-date(date)"/>
                    by <xsl:value-of select="poster"/></font>
                  </p>
                      <xsl:choose>
                        <xsl:when test="@category='alpha'">
                          <img class="newsicon" src="/images/icon-alpha.gif" alt="AlphaServer GS160"/>
                        </xsl:when>
                        <xsl:when test="@category='kde'">
                          <img class="newsicon" src="/images/icon-kde.png" alt="KDE"/>
                        </xsl:when>
                        <xsl:when test="@category='gentoo'">
                          <img class="newsicon" src="/images/icon-gentoo.png" alt="gentoo"/>
                        </xsl:when>
                        <xsl:when test="@category='main'">
                          <img class="newsicon" src="/images/icon-stick.png" alt="stick man"/>
                        </xsl:when>
                        <xsl:when test="@category='ibm'">
                          <img class="newsicon" src="/images/icon-ibm.gif" alt="IBM"/>
                        </xsl:when>
                        <xsl:when test="@category='linux'">
                          <img class="newsicon" src="/images/icon-penguin.png" alt="Tux the Penguin"/>
                        </xsl:when>
                        <xsl:when test="@category='moo'">
                          <img class="newsicon" src="/images/icon-cow.png" alt="Larry the Cow"/>
                        </xsl:when>
                        <xsl:when test="@category='nvidia'">
                          <img class="newsicon" src="/images/icon-nvidia.png" alt="nvidia"/>
                        </xsl:when>
                        <xsl:when test="document(.)/news/@category='freescale'">
                          <img class="newsicon" src="/images/icon-freescale.gif" alt="Freescale Semiconductor"/>
                        </xsl:when>
                      </xsl:choose>

                    <span class="newsitem">
                      <xsl:choose>
                        <xsl:when test="body">
                          <xsl:apply-templates select="body"/>
                        </xsl:when>
                        <xsl:when test="section">
                          <xsl:apply-templates select="section"/>
                        </xsl:when>
                      </xsl:choose>
                    </span>
              </div>
              </xsl:when>
              <xsl:when test="/email">
                <xsl:apply-templates select="/email/body"/>
              </xsl:when>
            </xsl:choose>
            <br/>
            <table border="0" class="content">
              <tr>
                <td>
                  <xsl:apply-templates select="chapter"/>
                </td>
              </tr>
            </table>
            <br/>
            <xsl:if test="/mainpage/license">
              <xsl:apply-templates select="license" />
            </xsl:if>
            <br/>
            <!--content end-->
    </td>
    <td width="1%" bgcolor="#dddaec" valign="top">
      <xsl:call-template name="rhcol"/>
    </td>
  </tr>
  <tr lang="en">
    <td align="right" class="infohead" colspan="3">
      Copyright 2001-2005 Gentoo Foundation, Inc.  Questions, Comments, Corrections?  Email <a class="highlight" href="mailto:www@gentoo.org">www@gentoo.org</a>.
    </td>
  </tr>
</table>

</body>
<xsl:text disable-output-escaping="yes">&lt;/html&gt;</xsl:text>
</xsl:template>

<!-- News items -->
<xsl:template match="newsitems">
  <xsl:apply-templates select="news"/>
</xsl:template>

<!-- News template, child of newsitems -->
<xsl:template match="news">
<table width="100%" border="0" cellspacing="5" cellpadding="0">
  <tr>
    <td colspan="2" class="ncontent" bgcolor="#bbffbb">
      <p class="note">
        <font color="#7a5ada">
          <b><xsl:value-of select="title"/></b>
        </font>
      </p>
    </td>
  </tr>
  <tr>
    <xsl:choose>
      <xsl:when test="@align='left'">
        <td rowspan="2" valign="top" width="1">
          <img src="{@graphic}"/>
        </td>
        <td class="alttext" lang="en">
          <font color="#808080">
            Posted by <xsl:value-of select="poster"/> on <xsl:value-of select="date"/>
          </font>
        </td>
      </xsl:when>
      <xsl:otherwise>
        <td class="alttext" lang="en">
          <font color="#808080">
            Posted by <xsl:value-of select="poster"/> on <xsl:value-of select="date"/>
          </font>
        </td>
        <td rowspan="2" valign="top" width="1">
          <img src="{@graphic}"/>
        </td>
      </xsl:otherwise>
    </xsl:choose>
  </tr>
  <tr>
    <td class="content" valign="top">
      <xsl:apply-templates select="body"/>
    </td>
  </tr>
</table>
<br/>
<table width="100%">
  <tr>
    <td height="1" bgcolor="#c0c0c0"/>
  </tr>
</table>
<br/>
</xsl:template>

<!-- Mail template -->
<xsl:template match="mail">
<a href="mailto:{@link}"><xsl:value-of select="."/></a>
</xsl:template>

<!-- Mail inside <author>...</author> -->
<xsl:template match="/guide/author/mail|/book/author/mail">
<b>
  <a class="altlink" href="mailto:{@link}"><xsl:value-of select="."/></a>
</b>
</xsl:template>

<!-- Author -->
<xsl:template match="author">
<xsl:apply-templates/>
  <xsl:if test="@title">
    <xsl:if test="$style != 'printable'">
      <br/>
    </xsl:if>
    <xsl:if test="$style = 'printable'">&#160;</xsl:if>
    <i><xsl:value-of select="@title"/></i>
  </xsl:if>
  <br/>
  <xsl:if test="$style != 'printable' and position()!=last()">
    <br/>
  </xsl:if>
</xsl:template>

<!-- Chapter -->
<xsl:template match="chapter">
<xsl:variable name="chid"><xsl:number/></xsl:variable>
<xsl:choose>
  <xsl:when test="title">
    <p class="chaphead">
      <xsl:if test="@id">
        <a name="{@id}"/>
      </xsl:if>
      <span class="chapnum">
        <a name="doc_chap{$chid}"><xsl:number/>. </a>
      </span>
      <xsl:value-of select="title"/>
    </p>
  </xsl:when>
  <xsl:otherwise>
    <xsl:if test="/guide">
      <p class="chaphead">
        <span class="chapnum">
          <a name="doc_chap{$chid}"><xsl:number/>.</a>
        </span>
      </p>
    </xsl:if>
  </xsl:otherwise>
</xsl:choose>
<xsl:apply-templates select="body">
  <xsl:with-param name="chid" select="$chid"/>
</xsl:apply-templates>
<xsl:apply-templates select="section">
  <xsl:with-param name="chid" select="$chid"/>
</xsl:apply-templates>
</xsl:template>


<!-- Section template -->
<xsl:template match="section">
<xsl:param name="chid"/>
<xsl:if test="title">
  <xsl:variable name="sectid">doc_chap<xsl:value-of select="$chid"/>_sect<xsl:number/></xsl:variable>
  <xsl:if test="@id">
    <a name="{@id}"/>
  </xsl:if>
  <p class="secthead">
    <a name="{$sectid}"><xsl:value-of select="title"/></a>
  </p>
</xsl:if>
<xsl:apply-templates select="body">
  <xsl:with-param name="chid" select="$chid"/>
</xsl:apply-templates>
</xsl:template>

<!-- Figure template -->
<xsl:template match="figure">
<xsl:param name="chid"/>
<xsl:variable name="fignum"><xsl:number level="any" from="chapter" count="figure"/></xsl:variable>
<xsl:variable name="figid">doc_chap<xsl:value-of select="$chid"/>_fig<xsl:value-of select="$fignum"/></xsl:variable>
<xsl:variable name="llink">
  <xsl:choose>
    <xsl:when test="starts-with(@link,'http://www.gentoo.org/')">
      <xsl:value-of select="substring-after(@link, 'http://www.gentoo.org')"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="@link"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:variable>
<br/>
<a name="{$figid}"/>
<table cellspacing="0" cellpadding="0" border="0">
  <tr>
    <td bgcolor="#7a5ada">
      <p class="codetitle">
        <xsl:choose>
          <xsl:when test="@caption">
            <xsl:value-of select="func:gettext('Figure')"/>&#160;<xsl:value-of select="$chid"/>.<xsl:value-of select="$fignum"/><xsl:value-of select="func:gettext('SpaceBeforeColon')"/>: <xsl:value-of select="@caption"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="func:gettext('Figure')"/>&#160;<xsl:value-of select="$chid"/>.<xsl:value-of select="$fignum"/>
          </xsl:otherwise>
        </xsl:choose>
      </p>
    </td>
  </tr>
  <tr>
    <td align="center" bgcolor="#ddddff">
      <xsl:choose>
        <xsl:when test="@short">
          <img src="{$llink}" alt="Fig. {$fignum}: {@short}"/>
        </xsl:when>
        <xsl:otherwise>
          <img src="{$llink}" alt="Fig. {$fignum}"/>
        </xsl:otherwise>
      </xsl:choose>
    </td>
  </tr>
</table>
<br/>
</xsl:template>

<!--figure without a caption; just a graphical element-->
<xsl:template match="fig">
<center>
  <xsl:choose>
    <xsl:when test="@linkto">
      <a href="{@linkto}"><img border="0" src="{@link}" alt="{@short}"/></a>
    </xsl:when>
    <xsl:otherwise>
      <img src="{@link}" alt="{@short}"/>
    </xsl:otherwise>
  </xsl:choose>
</center>
</xsl:template>

<!-- Line break -->
<xsl:template match="br">
<br/>
</xsl:template>

<!-- Note -->
<xsl:template match="note">
<table class="ncontent" width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td bgcolor="#bbffbb">
      <p class="note">
        <b><xsl:value-of select="func:gettext('Note')"/>: </b>
        <xsl:apply-templates/>
      </p>
    </td>
  </tr>
</table>
</xsl:template>

<!-- Important item -->
<xsl:template match="impo">
<table class="ncontent" width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td bgcolor="#ffffbb">
      <p class="note">
        <b><xsl:value-of select="func:gettext('Important')"/>: </b>
        <xsl:apply-templates/>
      </p>
    </td>
  </tr>
</table>
</xsl:template>

<!-- Warning -->
<xsl:template match="warn">
<table class="ncontent" width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td bgcolor="#ffbbbb">
      <p class="note">
        <b><xsl:value-of select="func:gettext('Warning')"/>: </b>
        <xsl:apply-templates/>
      </p>
    </td>
  </tr>
</table>
</xsl:template>

<!-- Code note -->
<xsl:template match="codenote">
<span class="comment">
  <xsl:if test='not(starts-with(., "("))'>(</xsl:if>
  <xsl:apply-templates/>
  <xsl:if test='not(starts-with(., "("))'>)</xsl:if>
</span>
</xsl:template>

<!-- Regular comment -->
<xsl:template match="comment">
<span class="comment">
  <xsl:apply-templates/>
</span>
</xsl:template>

<!-- User input -->
<xsl:template match="i">
<span class="input"><xsl:apply-templates/></span>
</xsl:template>

<!-- Bold -->
<xsl:template match="b">
<b><xsl:apply-templates/></b>
</xsl:template>

<!-- Brite -->
<xsl:template match="brite">
<font color="#ff0000">
  <b><xsl:apply-templates/></b>
</font>
</xsl:template>

<!-- Body inside email -->
<xsl:template match="/email/body">
<table border="0">
  <tr>
    <td>
      <span class="content">
        <p class="secthead">
          Subject: <xsl:value-of select="/email/subject"/>
        </p>
        <p class="secthead">
          <font color="#000000">
            List: <xsl:value-of select="/email/list"/> at gentoo.org<br/>
            Date: <xsl:value-of select="/email/date"/><br/>
            From: <xsl:value-of select="/email/from"/><br/><br/>
            <xsl:if test="/email/nav/prev">
              <xsl:for-each select="/email/nav/prev[position()=1]/text()">
                <xsl:variable name="navloc" select="."/>
                <xsl:variable name="navfile">/dyn/lists/<xsl:value-of select="/email/list"/>/<xsl:value-of select="."/>.xml</xsl:variable>
                Previous: <a href="{$navfile}"><xsl:value-of select="document($navfile)/email/subject"/></a><br/>
              </xsl:for-each>
            </xsl:if>
            <xsl:if test="/email/nav/next">
              <xsl:for-each select="/email/nav/next[position()=1]/text()">
                <xsl:variable name="navloc" select="."/>
                <xsl:variable name="navfile">/dyn/lists/<xsl:value-of select="/email/list"/>/<xsl:value-of select="."/>.xml</xsl:variable>
                Next: <a href="{$navfile}"><xsl:value-of select="document($navfile)/email/subject"/></a><br/>
              </xsl:for-each>
            </xsl:if>
            <xsl:if test="/email/in-reply-to">
              <xsl:for-each select="/email/in-reply-to[position()=1]/text()">
                <xsl:variable name="irtloc" select="."/>
                <xsl:variable name="irtfile">/dyn/lists/<xsl:value-of select="/email/list"/>/<xsl:value-of select="."/>.xml</xsl:variable>
                In Reply To: <a href="{$irtfile}"><xsl:value-of select="document($irtfile)/email/subject"/></a><br/>
              </xsl:for-each>
            </xsl:if>
            <xsl:if test="/email/replies">
              <br/>Replies to this message:<br/>
              <xsl:for-each select="/email/replies/reply/text()">
                <xsl:variable name="rloc" select="."/>
                <xsl:variable name="rfile">/dyn/lists/<xsl:value-of select="/email/list"/>/<xsl:value-of select="."/>.xml</xsl:variable>
                &#160;<a href="{$rfile}"><xsl:value-of select="document($rfile)/email/subject"/></a><br/>
              </xsl:for-each>
            </xsl:if>
          </font>
        </p>
      </span>
      <pre>
        <xsl:apply-templates/>
      </pre>
    </td>
  </tr>
</table>
</xsl:template>

<!-- Body -->
<xsl:template match="body">
<xsl:param name="chid"/>
<xsl:apply-templates>
  <xsl:with-param name="chid" select="$chid"/>
</xsl:apply-templates>
</xsl:template>

<!-- Command or input, not to use inside <pre> -->
<xsl:template match="c">
<span class="code"><xsl:apply-templates/></span>
</xsl:template>

<!-- Box with small text -->
<xsl:template match="box">
<p class="infotext"><xsl:apply-templates/></p>
</xsl:template>

<!-- Preserve whitespace, aka Code Listing -->
<xsl:template match="pre">
<xsl:param name="chid"/>
<xsl:variable name="prenum"><xsl:number level="any" from="chapter" count="pre"/></xsl:variable>
<xsl:variable name="preid">doc_chap<xsl:value-of select="$chid"/>_pre<xsl:value-of select="$prenum"/></xsl:variable>
<a name="{$preid}"/>
<table class="ntable" width="100%" cellspacing="0" cellpadding="0" border="0">
  <tr>
    <td bgcolor="#7a5ada">
      <p class="codetitle">
      <xsl:value-of select="func:gettext('CodeListing')"/>&#160;<xsl:if test="$chid"><xsl:value-of select="$chid"/>.</xsl:if><xsl:value-of select="$prenum"/>
      <xsl:if test="@caption">
        <xsl:value-of select="func:gettext('SpaceBeforeColon')"/>: <xsl:value-of select="@caption"/>
      </xsl:if>
      </p>
    </td>
  </tr>
  <tr>
    <td bgcolor="#ddddff">
      <pre>
        <xsl:apply-templates/>
      </pre>
    </td>
  </tr>
</table>
</xsl:template>

<!-- Path -->
<xsl:template match="path">
<span class="path"><xsl:value-of select="."/></span>
</xsl:template>

<!-- Url -->
<xsl:template match="uri">
<!-- expand templates to handle things like <uri link="http://bar"><c>foo</c></uri> -->
<xsl:choose>
  <xsl:when test="@link">
    <xsl:choose>
      <xsl:when test="($TTOP = 'sections') and (starts-with(@link, '?'))">
        <!-- Handbook link pointing to another part/chapter when viewing a single page,
             cannot be a link because we have no idea where to link to
             Besides, we have no way of knowing the language unless told via a param -->
          <xsl:variable name="nolink"><xsl:value-of select="func:gettext('hb_file', $glang)"/></xsl:variable>
          <span title="{$nolink}"><font color="#404080">(<xsl:apply-templates/>)</font></span>
      </xsl:when>
      <xsl:when test="($TTOP = 'book') and ($full = 0) and (starts-with(@link, '?'))">
        <!-- Handbook link pointing to another part/chapter, normal case -->
        <xsl:choose>
          <xsl:when test="$style != 'printable'">
            <a href="{$LINK}{@link}"><xsl:apply-templates/></a>
          </xsl:when>
          <xsl:otherwise>
            <a href="{$LINK}{@link}&amp;style=printable"><xsl:apply-templates/></a>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="($TTOP = 'book') and ($full = 1) and (starts-with(@link, '?'))">
        <!-- Handbook link pointing to another part/chapter
             Handbook is being rendered in a single page (full=1)
             Hence link needs to be rewritten as a local one
             i.e. ?part=1&chap=3#doc_chap1 must become #book_part1_chap3__chap1   Case 1a
             i.e. ?part=1&chap=3#anID      must become #anID                      Case 1b
             or   ?part=1&chap=3           must become #book_part1_chap3          Case 2
             or   ?part=2                  must become #book_part2                Case 3-->
        <xsl:choose>
          <xsl:when test="contains(@link, 'chap=') and contains(@link, '#doc_')">
            <!-- Link points inside a chapter  (Case 1a)-->
            <xsl:param name="linkpart" select="substring-after(substring-before(@link, '&amp;'), '=')" />
            <xsl:param name="linkchap" select="substring-before(substring-after(substring-after(@link, '&amp;'), '='), '#doc_')" />
            <xsl:param name="linkanch" select="substring-after(@link, '#doc_')" />
            <a href="#book_part{$linkpart}_chap{$linkchap}__{$linkanch}"><xsl:apply-templates /></a>
          </xsl:when>
          <xsl:when test="contains(@link, 'chap=') and contains(@link, '#')">
            <!-- Link points inside a chapter via an ID (Case 1b)
                 (IDs are expected to be unique throughout a handbook) -->
            <xsl:param name="linkanch" select="substring-after(@link, '#')" />
            <a href="#{$linkanch}"><xsl:apply-templates /></a>
          </xsl:when>
          <xsl:when test="contains(@link, 'chap=')">
            <!-- Link points to a chapter  (Case 2)-->
            <xsl:param name="linkpart" select="substring-after(substring-before(@link, '&amp;'), '=')" />
            <xsl:param name="linkchap" select="substring-after(substring-after(@link, '&amp;'), '=')" />
            <a href="#book_part{$linkpart}_chap{$linkchap}"><xsl:apply-templates /></a>
          </xsl:when>
          <xsl:otherwise>
            <!-- Link points to a part  (Case 3)-->
            <xsl:param name="linkpart" select="substring-after(@link, '=')" />
            <a href="#book_part{$linkpart}"><xsl:apply-templates/></a>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="($TTOP = 'book') and ($full = 1) and (starts-with(@link, '#'))">
        <!-- Handbook link pointing to another place in same part/chapter
             Handbook is being rendered in a single page (full=1)
             Hence link needs to be rewritten as an internal one that is unique
             for the whole handbook, i.e.
             #doc_part1_chap3 becomes #book_{UNIQUEID}_part1_chap3, but
             #anything_else_like_an_ID is left unchanged (IDs are expected to be unique throughout a handbook)-->
        <xsl:choose>
          <xsl:when test="starts-with(@link, '#doc_')">
            <xsl:param name="locallink" select="substring-after(@link, 'doc_')" />
            <a href="#book_{generate-id(/)}_{$locallink}"><xsl:apply-templates /></a>
          </xsl:when>
          <xsl:otherwise>
            <a href="{@link}"><xsl:apply-templates/></a>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <!-- Strip http://www.gentoo.org from links but leave links to viewcvs intact
             Has no effect on actual www.g.o but helps when surfing on a local copy -->
        <xsl:variable name="llink">
          <xsl:choose>
            <xsl:when test="starts-with(@link, 'http://www.gentoo.org/cgi-bin/')"><xsl:value-of select="@link" /></xsl:when>
            <xsl:when test="starts-with(@link, 'http://www.gentoo.org/')"><xsl:value-of select="substring-after(@link, 'http://www.gentoo.org')" /></xsl:when>
            <xsl:otherwise><xsl:value-of select="@link" /></xsl:otherwise>
          </xsl:choose>
        </xsl:variable>

        <!-- Now, insert style=printable in the URL if necessary -->
        <xsl:variable name="alink">
          <xsl:choose>
          <xsl:when test="$style != 'printable'  or  contains($llink, 'style=printable')">
            <!-- Not printable style or style=printable already in URL, copy link -->
            <xsl:value-of select="$llink" />
          </xsl:when>
          <xsl:when test="contains($llink, '://')">
            <!-- External link, copy link -->
            <xsl:value-of select="$llink" />
          </xsl:when>
          <xsl:when test="starts-with($llink, '#')">
            <!-- Anchor, copy link -->
            <xsl:value-of select="$llink" />
          </xsl:when>
          <xsl:otherwise>
            <!--  We should have eliminated all other cases,
                  style printable, local link, then insert ?style=printable -->
            <xsl:choose>
              <xsl:when test="starts-with($llink, '?')">
                <xsl:value-of select="concat( '?style=printable&amp;', substring-after($llink, '?'))" />
              </xsl:when>
              <xsl:when test="contains($llink, '.xml?')">
                <xsl:value-of select="concat(substring-before($llink, '.xml?'), '.xml?style=printable&amp;', substring-after($llink, '.xml?'))" />
              </xsl:when>
              <xsl:when test="contains($llink, '.xml#')">
                <xsl:value-of select="concat(substring-before($llink, '.xml#'), '.xml?style=printable#', substring-after($llink, '.xml#'))" />
              </xsl:when>
              <xsl:when test="substring-after($llink, '.xml') = ''">
                <xsl:value-of select="concat($llink, '?style=printable')" />
              </xsl:when>
              <xsl:otherwise>
                <!-- Have I forgotten anything?
                     Copy link -->
                <xsl:value-of select="$llink" />
              </xsl:otherwise>
            </xsl:choose>
          </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <a href="{$alink}"><xsl:apply-templates/></a>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:when>
  <xsl:otherwise>
    <xsl:variable name="loc" select="."/>
    <a href="{$loc}"><xsl:apply-templates/></a>
  </xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- Paragraph -->
<xsl:template match="p">
<xsl:param name="chid"/>
<xsl:choose>
  <xsl:when test="@class">
    <p class="{@class}">
      <xsl:apply-templates>
        <xsl:with-param name="chid" select="$chid"/>
      </xsl:apply-templates>
    </p>
  </xsl:when>
  <xsl:otherwise>
    <p>
      <xsl:apply-templates>
        <xsl:with-param name="chid" select="$chid"/>
      </xsl:apply-templates>
    </p>
  </xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- Emphasize -->
<xsl:template match="e">
  <span class="emphasis"><xsl:apply-templates/></span>
</xsl:template>

<!-- Table -->
<xsl:template match="table">
<table class="ntable">
  <xsl:apply-templates/>
</table>
</xsl:template>

<!-- Table Row -->
<xsl:template match="tr">
<tr>
  <xsl:apply-templates/>
</tr>
</xsl:template>

<!-- Table Item -->
<xsl:template match="ti">
<td class="tableinfo">
  <xsl:apply-templates/>
</td>
</xsl:template>

<!-- Table Heading -->
<xsl:template match="th">
<td class="infohead">
  <b>
    <xsl:apply-templates/>
  </b>
</td>
</xsl:template>

<!-- Unnumbered List -->
<xsl:template match="ul">
<ul>
  <xsl:apply-templates/>
</ul>
</xsl:template>

<!-- Ordered List -->
<xsl:template match="ol">
<ol>
  <xsl:apply-templates/>
</ol>
</xsl:template>

<!-- List Item -->
<xsl:template match="li">
<li>
  <xsl:apply-templates/>
</li>
</xsl:template>

<!-- NOP -->
<xsl:template match="ignoreinemail">
<xsl:apply-templates/>
</xsl:template>

<!-- NOP -->
<xsl:template match="ignoreinguide">
</xsl:template>

<!-- License Tag -->
<xsl:template match="license">
<p class="copyright">
  <xsl:apply-templates select="func:gettext('License')"/>
</p>
</xsl:template>

<!-- GLSA Index -->
<xsl:template match="glsaindex">
  <xsl:apply-templates select="document('/dyn/glsa-index.xml')/guide/chapter[1]/section[1]/body"/>
</xsl:template>

<!-- GLSA Latest (max 10) -->
<xsl:template match="glsa-latest">
  <xsl:variable name="src" select="'/dyn/glsa-index.xml'"/>
  <table>
  <xsl:for-each select="document($src)/guide/chapter[1]/section[1]/body/table[1]/tr[position()&lt;11]">
    <tr><xsl:apply-templates/></tr>
  </xsl:for-each>
  </table>
</xsl:template>


<xsl:template name="contentdate">
  <!-- Update datestamp -->
  <xsl:value-of select="concat(func:gettext('Updated'),' ')"/>
  <xsl:choose>
    <xsl:when test="/book">
      <!-- In a book: look for max(/date, include_files/sections/date) -->
      <xsl:for-each select="/book/part/chapter/include">
        <xsl:sort select="document(@href)/sections/date" order="descending" />
        <xsl:if test="position() = 1">
          <!-- Compare the max(date) from included files with the date in the master file
               Of course, XSLT 1.0 knows no string comparison operator :-(
               So we build a node set with the two dates and we sort it.
            -->
          <xsl:variable name="theDates">
            <xsl:element name="bookDate">
              <xsl:value-of select="/book/date"/>
            </xsl:element>
            <xsl:element name="maxChapterDate">
              <xsl:value-of select="document(@href)/sections/date"/>
            </xsl:element>
          </xsl:variable>
          <xsl:variable name="sortedDates">  
            <xsl:for-each select="exslt:node-set($theDates)/*">  
              <xsl:sort select="." order="descending" />
              <xsl:copy-of select="."/>
            </xsl:for-each>   
          </xsl:variable>
          <!-- First date is the one we want -->
          <xsl:value-of select="func:format-date(exslt:node-set($sortedDates)/*[position()=1])"/>
        </xsl:if>
      </xsl:for-each>
    </xsl:when>
    <xsl:when test="/guide or /sections">
      <xsl:value-of select="func:format-date(//date[1])"/>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<xsl:template name="rhcol">
<!-- Right-hand column with date/authors/ads -->
  <table border="0" cellspacing="4px" cellpadding="4px">
    <!-- Add a "printer-friendly" button when link attribute exists -->
    <xsl:if test="/book/@link or /guide/@link">
     <tr>
      <td class="topsep" align="center">
        <p class="altmenu">
        <xsl:variable name="PrintTip"><xsl:value-of select="func:gettext('PrintTip')"/></xsl:variable>
        <xsl:if test="/book">
         <xsl:if test="$full=1">
          <a title="{$PrintTip}" class="altlink" href="{/book/@link}?full=1&amp;style=printable"><xsl:value-of select="func:gettext('Print')"/></a>
         </xsl:if>
         <xsl:if test="$full=0">
          <a title="{$PrintTip}" class="altlink" href="{/book/@link}?part={$part}&amp;chap={$chap}&amp;style=printable"><xsl:value-of select="func:gettext('Print')"/></a>
         </xsl:if>
        </xsl:if>
        <xsl:if test="/guide">
          <a title="{$PrintTip}" class="altlink" href="{/guide/@link}?style=printable"><xsl:value-of select="func:gettext('Print')"/></a>
        </xsl:if>
        </p>
      </td>
     </tr>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="/book/date or /guide/date or /sections/date">
        <tr>
          <td align="center" class="topsep">
            <p class="alttext">
            <xsl:call-template name="contentdate"/>
            </p>
          </td>
        </tr>
      </xsl:when>
      <xsl:when test="/mainpage/date">
        <tr>
          <td align="center" class="topsep">
            <p class="alttext">
            <xsl:value-of select="concat(func:gettext('Updated'),' ')"/>
            <xsl:value-of select="func:format-date(/mainpage/date)"/>
            </p>
          </td>
        </tr>
      </xsl:when>
      <xsl:when test="/news/date">
        <tr>
          <td align="center" class="topsep">
            <p class="alttext">
            <xsl:value-of select="concat(func:gettext('Updated'),' ')"/>
            <xsl:value-of select="func:format-date(/news/date)"/>
            </p>
          </td>
        </tr>
      </xsl:when>
    </xsl:choose>
    <xsl:if test="/book/abstract[normalize-space(.)] or /guide/abstract[normalize-space(.)]">
      <tr>
        <td class="topsep">
          <p class="alttext">
            <!-- Abstract (summary) of the document -->
            <b><xsl:value-of select="func:gettext('Summary')"/>: </b>
            <xsl:apply-templates select="abstract"/>
          </p>
        </td>
      </tr>
    </xsl:if>
    <xsl:if test="/book/author or /guide/author">
    <tr>
      <td class="topsep">
        <p class="alttext">
          <!-- Authors -->
          <xsl:apply-templates select="/guide/author|/book/author"/>
        </p>
      </td>
    </tr>
    </xsl:if>

      <tr lang="en">
      <td align="center" class="topsep">
        <p class="alttext">
          <b>Donate</b> to support our development efforts.
        </p>

        <form action="https://www.paypal.com/cgi-bin/webscr" method="post">
          <input type="hidden" name="cmd" value="_xclick"/>
          <input type="hidden" name="business" value="paypal@gentoo.org"/>
          <input type="hidden" name="item_name" value="Gentoo Linux Support"/>
          <input type="hidden" name="item_number" value="1000"/>
          <input type="hidden" name="image_url" value="/images/paypal.png"/>
          <input type="hidden" name="no_shipping" value="1"/>
          <input type="hidden" name="return" value="http://www.gentoo.org"/>
          <input type="hidden" name="cancel_return" value="http://www.gentoo.org"/>

          <input type="image" src="http://images.paypal.com/images/x-click-but21.gif" name="submit" alt="Make payments with PayPal - it's fast, free and secure!"/>
        </form>
      </td>
    </tr>
    <tr lang="en">
    <td align="center" class="topsep">
            <a href="http://www.vr.org">
	    <img src="/images/vr-ad.png" width="125" height="144" alt="Gentoo Centric Hosting: vr.org" border="0"/>
        </a>
	    <p class="alttext">
	      <a href="http://www.vr.org/">VR Hosted</a>
	    </p>
    </td>
    </tr>
    <tr lang="en">
      <td align="center" class="topsep">
      <a href="http://www.tek.net" target="_top">
        <img src="/images/tek-gentoo.gif" width="125" height="125" alt="Tek Alchemy" border="0"/>
      </a>
      <p class="alttext">
	  <a href="http://www.tek.net/">Tek Alchemy</a>
      </p>
      </td>
    </tr>
    <tr lang="en">
    <td align="center" class="topsep">
      <a href="http://www.sevenl.net" target="_top">
        <img src="/images/sponsors/sevenl.gif" width="125" height="144" alt="SevenL.net" border="0"/>
      </a>
      <p class="alttext">
	  <a href="http://www.sevenl.net/">SevenL.net</a>
      </p>
    </td>
    </tr>
    <tr lang="en">
    <td align="center" class="topsep">
        <a href="http://www.phparch.com/bannerclick.php?AID=68&amp;BID=1&amp;BT=127929" target="_top">
          <img src="/images/phpa-gentoo.gif" width="125" height="144" alt="php|architect" border="0"/>
      </a>
      <p class="alttext">
	  <a href="http://www.phparch.com/bannerclick.php?AID=68&amp;BID=1&amp;BT=127929">php|architect</a>
      </p>
    </td>
    </tr>
    <tr>
    <td align="center" class="topsep"/>
    </tr>
  </table>
</xsl:template>

<xsl:template name="commonHTMLheader">
  <xsl:choose>
    <xsl:when test="string-length($glang)>1">
      <!-- Output html="$LANG" if possible -->
      <!-- Do not output default "en" because many non-English pages have no lang attribute
           and I'd rather not output any lang at all than send "en" for German pages e.g. -->
      <!-- Language code and sub-code are case-insensitive and should be separated by a hyphen -->
      <xsl:text disable-output-escaping="yes">
        &lt;HTML lang="</xsl:text><xsl:value-of select="translate($glang,'_','-')"/><xsl:text disable-output-escaping="yes">"&gt;
      </xsl:text>
    </xsl:when>
    <xsl:otherwise>
      <xsl:text disable-output-escaping="yes">
        &lt;HTML&gt;
      </xsl:text>
    </xsl:otherwise>
  </xsl:choose>
  <xsl:text disable-output-escaping="yes">
    &lt;head&gt;
    &lt;meta http-equiv="Content-Type" content="text/html; charset=UTF-8"&gt;
    &lt;link title="new" rel="stylesheet" href="/css/main.css?d=20050605" type="text/css"&gt;
    &lt;link REL="shortcut icon" HREF="http://www.gentoo.org/favicon.ico" TYPE="image/x-icon"&gt;
 </xsl:text>
</xsl:template>

</xsl:stylesheet>
