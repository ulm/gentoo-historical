<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output encoding="UTF-8" method="html" indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"/>
	<xsl:preserve-space elements="pre"/>
	<xsl:template match="img">
		<img src="{@src}"/>
	</xsl:template>
	<xsl:template match="/guide">
	<html>
	<head>
	<link title="new" rel="stylesheet" href="/css/main.css" type="text/css"/>
	<link REL="shortcut icon" HREF="http://ppc.gentoo.org/favicon.ico" TYPE="image/x-icon"/>
	<title>Gentoo Linux on PowerPC -- News</title> 
	</head>
	<body style="margin-left:0px;margin-top:0px;" bgcolor="#ffffff">
	<table width="100%" border="0" cellspacing="0" cellpadding="0">
	<tr>
	<td valign="top" height="125" bgcolor="#45347b">
		<table cellspacing="0" cellpadding="0" border="0" width="193">
			<tr>
				<td class="logobg" valign="top" align="center" height="88">
					<a href="/">
						<img border="0" src="/images/gtop-s.jpg" alt="Gentoo Logo"/>
					</a>
				</td>
			</tr>
			<tr>
				<td class="logobg" valign="top" align="center" height="36">
					<a href="/">
						<img border="0" src="/images/gbot-s.gif" alt="Gentoo Logo Side"/>
					</a>
				</td>
</tr>
		</table>
	
	
	</td>
</tr>
	<tr>
		<td valign="top" align="right" colspan="1" bgcolor="#ffffff">
<!--content begin-->
			<table border="0" cellspacing="0" cellpadding="0" width="100%">
				<tr>
					<td width="99%" class="content" valign="top" align="left">
						<br/>
						<p class="dochead">
                      <xsl:choose>
                        <xsl:when test="/guide/subtitle">
			<xsl:value-of select="/guide/title"/>: <xsl:value-of select="/guide/subtitle"/></xsl:when>
                        <xsl:otherwise>
                          <xsl:value-of select="/guide/title"/>
                        </xsl:otherwise>
                      </xsl:choose>
                    </p>
                    <form name="contents" action="http://ppc.gentoo.org"><b>Contents</b>:
	<select name="url" size="1" OnChange="location.href=form.url.options[form.url.selectedIndex].value" style="font-family:Arial,Helvetica, sans-serif; font-size:10"><xsl:for-each select="chapter"><xsl:variable name="chapid">doc_chap<xsl:number/></xsl:variable><option value="#{$chapid}"><xsl:number/>. <xsl:value-of select="title"/></option>

				</xsl:for-each></select></form>
                    <xsl:apply-templates select="chapter"/>
                    <br/>
                    <br/>
<!--content end-->
                  </td>
                  <td width="1%" bgcolor="#dddaec" valign="top">
                    <table border="0" cellspacing="5" cellpadding="0">
                      <tr>
                        <td>
                          <img src="/images/line.gif" alt="line"/>
                        </td>
                      </tr>
                      <tr>
                        <td align="center" class="alttext">
				Updated <xsl:value-of select="/guide/date"/>
			</td>
                      </tr>
		      <tr>
		      	<td>
				<img src="/images/line.gif" alt="line"/>
                        </td>
                      </tr>
                      <tr>
                        <td class="alttext">
                          <xsl:apply-templates select="/guide/author"/>
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <img src="/images/line.gif" alt="line"/>
                        </td>
                      </tr>
                      <tr>
                        <td class="alttext"><b>Summary:</b>&#160;<xsl:apply-templates select="abstract"/></td>
                      </tr>
                      <tr>
                        <td>
                          <img src="/images/line.gif" alt="line"/>
                        </td>
                      </tr>
                <tr>
                  <td align="center">
<!-- Begin PayPal Logo -->
		<p class="alttext"><b>Donate</b> to support our development efforts.</p>
                    <form action="https://www.paypal.com/cgi-bin/webscr" method="post">
                      <input type="hidden" name="cmd" value="_xclick"/>
                      <input type="hidden" name="business" value="drobbins@gentoo.org"/>
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
                <tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr>
			<tr>
			<td align="center">
				<a href="http://www.cafeshops.com/cp/store.aspx?s=gentoolinux">
				<img src="/images/store.png" alt="The Gentoo Linux Store" border="0"/>
				</a>
			</td>
		</tr>
		<tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr><tr>
                  <td align="center">
                    <p class="alttext">Win4Lin from <b>NeTraverse</b> lets you run Windows applications under Gentoo Linux at native speeds.</p>
		    <a href="http://www.netraverse.com/gentoo.htm" target="_top">
                      <img src="/images/netraverse-gentoo.gif" width="125" height="102" alt="Win4Lin at NeTraverse" border="0"/>
                    </a>
                     <p class="alttext"><a href="http://www.netraverse.com/gentoo.htm">Purchase Win4Lin "Gentoo Edition"</a> and you'll also get a special Gentoo discount. Every sale also helps support Gentoo Linux development :)</p>
                  </td>
		</tr>
		<tr>
                    <td>
                    <img src="/images/line.gif" alt="line"/>
                    </td>
                </tr>
		<tr>
                  <td align="center">
                    <a href="http://www.qksrv.net/click-477620-5032687" target="_top">
                      <img src="http://www.qksrv.net/image-477620-5032687" width="125" height="125" alt="DDR Memory at Crucial.com" border="0"/>
                    </a>
                    <p class="alttext">Purchase RAM from <b>Crucial.com</b> and a percentage of your sale will go towards further Gentoo Linux development.</p>
                  </td>
                </tr>
                <tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr>
			</table>
			</td>
			</tr>
			</table>
<!--Netscape 4.7 hack end-->
			</td>
          </tr>
          <tr>
            <td colspan="2" align="right" class="infohead" width="100%" bgcolor="#7a5ada">
			Copyright 2001-2003 Gentoo Technologies, Inc.  Questions, Comments, Corrections?  Email <a class="highlight" href="mailto:www@gentoo.org">www@gentoo.org</a>.
			</td>
          </tr>
        </table>
	  </body>
    </html>
  </xsl:template>
  <xsl:template match="/mainpage | /news | /email">
    <html>
      <head>
        <link title="new" rel="stylesheet" href="/css/main.css" type="text/css"/>
        <link REL="shortcut icon" HREF="/favicon.ico" TYPE="image/x-icon"/>
	<xsl:if test="/mainpage/@id='news'"><link rel="alternate" type="application/rss+xml" title="Gentoo Linux News RDF" href="http://ppc.gentoo.org/rdf/en/gentoo-news.rdf" /></xsl:if>
        <xsl:choose>
		<xsl:when test="/mainpage | /news">
			<title>Gentoo Linux -- <xsl:value-of select="title"/></title>
		</xsl:when>
		<xsl:when test="/email">
			<title><xsl:value-of select="subject"/></title>
		</xsl:when>
		</xsl:choose>
      </head>
      <body style="margin-left:0px;margin-top:0px;" bgcolor="#000000">
        <table border="0" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td valign="top" height="125" width="1%" bgcolor="#45347b">
              <table cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                  <td class="logobg" valign="top" align="center" height="88">
                    <a href="/">
                      <img border="0" src="/images/gtop-s.jpg" alt="Gentoo Logo"/>
                    </a>
                  </td>
                </tr>
                <tr>
                  <td class="logobg" valign="top" align="center" height="36">
                    <a href="/">
                      <img border="0" src="/images/gbot-s.gif" alt="Gentoo Logo Side"/>
                    </a>
                  </td>
                </tr>
              </table>
            </td>
            <td valign="bottom" align="left" bgcolor="#000000" colspan="2">
              <p class="menu">
	      	<xsl:choose>
			<xsl:when test="/mainpage/@id='news'">
				<a class="highlight" href="/">News</a> |
			</xsl:when>
			<xsl:otherwise>
				<a class="menulink" href="/">News</a> |
			</xsl:otherwise>
		</xsl:choose>
		<xsl:choose>
			<xsl:when test="/mainpage/@id='about'">
				<a class="highlight" href="/main/en/about.xml">About</a> |
			</xsl:when>
			<xsl:otherwise>
				<a class="menulink" href="/main/en/about.xml">About</a> |
			</xsl:otherwise>
		</xsl:choose>
<a class="menulink" href="http://forums.gentoo.org">Forums</a> |
		<xsl:choose>
			<xsl:when test="/mainpage/@id='lists'">
				<a class="highlight" href="/main/en/lists.xml">Lists</a> |
			</xsl:when>
			<xsl:otherwise>
				<a class="menulink" href="/main/en/lists.xml">Lists</a> |
			</xsl:otherwise>
		</xsl:choose>
			<a class="menulink" href="http://bugs.gentoo.org">Bugs</a> |
		<a class="menulink" href="http://www.cafeshops.com/cp/store.aspx?s=gentoolinux">Store</a> |
		<xsl:choose>
			<xsl:when test="/mainpage/@id='newsletter'">
				<a class="highlight" href="/news/en/gwn/gwn.xml"> GWN</a> |
			</xsl:when>
			<xsl:otherwise>
				<a class="menulink" href="/news/en/gwn/gwn.xml"> GWN</a> |
			</xsl:otherwise>
		</xsl:choose>
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
                  <td height="99%" valign="top" align="right">
<!--info goes here-->
                    <table cellspacing="0" cellpadding="5" border="0">
                      <tr>
                        <td valign="top">
                          <p class="altmenu">
				<!-- disable search for now
				Search gentoo.org:<table border="0" cellspacing="0" cellpadding="0"><tr><td>
				<form method="get" action="http://www.gentoo.org/cgi-bin/perlfect/search/search.pl">
					<input type="hidden" name="p" value="1"/>
					<input type="hidden" name="lang" value="en"/>
					<input type="hidden" name="include" value=""/>
					<input type="hidden" name="exclude" value=""/>
					<input type="hidden" name="penalty" value="0"/>
					<input type="hidden" name="mode" value="all"/>
					<input type="text" name="q"/>
				</form>
				</td></tr></table>
				<br/>	
				-->
				Resources:
				<a class="altlink" href="/main/en/lists.xml">Mailing lists</a>
				<br/>
				<a class="altlink" href="http://forums.gentoo.org">Discussion forums</a>
				<br/>
				<a class="hotlink" href="/dyn/index-cvs.xml">Daily CVS ChangeLog</a>
				<br/>
				<a class="altlink" href="http://bugs.gentoo.org">Bugzilla bug tracker</a>
				<br/>
				Miscellaneous Resources:
				<br/>
	
	<xsl:if test="/mainpage/@id='news'">
				<br/><br/>
				Older News:<br/>
				<xsl:for-each select="document('/proj/en/ppc/dyn/news-index.xml')/uris/uri[position()&gt;=7][position()&lt;20]/text()">
				<xsl:variable name="newsuri" select="."/>
				<a class="altlink" href="{$newsuri}"><xsl:value-of select="document(.)/news/title"/></a><br/>
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
            <td valign="top" align="right" bgcolor="#ffffff">
              <table border="0" cellspacing="5" cellpadding="0" width="100%">
                <tr>
                  <td valign="top" align="left">
                    <xsl:choose>
                      <xsl:when test="/mainpage/@id='news'">
                        <table class="content" cellpadding="4" width="100%" border="0">
                          <tr>
                            <td valign="top">
							<img src="/images/gentoo-new.gif" alt="new"/>
							</td>
                            <td valign="middle">
							We produce Gentoo Linux, a special flavor of Linux that can be automatically 
							optimized and customized for just about any application or need. Extreme
							performance, configurability and a top-notch user and developer community are
							all hallmarks of the Gentoo experience.
							To learn more, <b><a href="/main/en/about.xml">click here</a></b>.
				</td>
                          </tr>
                        </table>
                        <br/>
						<xsl:for-each select="document('/dyn/news-index.xml')/uris/uri[position()&lt;7]/text()">
                          <table class="content" cellpadding="4" width="100%" border="0">
                            <tr>
                              <td colspan="2" bgcolor="#7a5ada">
                                <font color="#ffffff">
                                  <b>
                                    <xsl:value-of select="document(.)/news/title"/>
                                  </b>
                                  <br/>
                                  <font size="-3">Posted on <xsl:value-of select="document(.)/news/date"/> by <xsl:value-of select="document(.)/news/poster"/></font>
                                </font>
                              </td>
                            </tr>
                            <tr>
                              <td width="100" align="center" valign="middle">
                                <xsl:choose>
                                  <xsl:when test="document(.)/news/@category='alpha'">
                                    <img src="/images/icon-alpha.gif" alt="AlphaServer GS160"/>
                                  </xsl:when>
	                                  <xsl:when test="document(.)/news/@category='kde'">
                                    <img src="/images/icon-kde.png" alt="KDE"/>
                                  </xsl:when>
									<xsl:when test="document(.)/news/@category='gentoo'">
                                    <img src="/images/icon-gentoo.png" alt="gentoo"/>
                                  </xsl:when>
                                  <xsl:when test="document(.)/news/@category='main'">
                                    <img src="/images/icon-stick.png" alt="stick man"/>
                                  </xsl:when>
                                  <xsl:when test="document(.)/news/@category='ibm'">
                                    <img src="/images/icon-ibm.gif" alt="ibm"/>
                                  </xsl:when>
                                  <xsl:when test="document(.)/news/@category='linux'">
                                    <img src="/images/icon-penguin.png" alt="tux"/>
                                  </xsl:when>
                                  <xsl:when test="document(.)/news/@category='moo'">
                                    <img src="/images/icon-cow.png" alt="Larry the Cow"/>
                                  </xsl:when>
                                  <xsl:when test="document(.)/news/@category='nvidia'">
                                    <img src="/images/icon-nvidia.png" alt="Nvidia"/>
                                  </xsl:when>
                                </xsl:choose>
                              </td>
                              <td valign="top">
                                <xsl:choose>
                                  <xsl:when test="document(.)/news/summary">
                                    <xsl:apply-templates select="document(.)/news/summary"/>
                                    <br/>
                                    <a href="{@external}">
                                      <b>(full story)</b>
                                    </a>
                                  </xsl:when>
                                  <xsl:otherwise>
                                    <xsl:apply-templates select="document(.)/news/body"/>
                                  </xsl:otherwise>
                                </xsl:choose>
                              </td>
                            </tr>
                          </table>
                          <br/>
                        </xsl:for-each>
                      </xsl:when>
                      <xsl:when test="/news">
                        <table class="content" cellpadding="4" width="100%" border="0">
                          <tr>
                            <td colspan="2" bgcolor="#7a5ada">
                              <font color="#ffffff">
                                <b>
                                  <xsl:value-of select="title"/>
                                </b>
                                <br/>
                                <font size="-3">Posted on <xsl:value-of select="date"/> by <xsl:value-of select="poster"/></font>
                              </font>
                            </td>
                          </tr>
                          <tr>
                            <td width="100" align="center" valign="top">
                              <xsl:choose>
                                 <xsl:when test="@category='alpha'">
                                    <img src="/images/icon-alpha.gif" alt="AlphaServer GS160"/>
                                  </xsl:when>
	                                  <xsl:when test="@category='kde'">
                                    <img src="/images/icon-kde.png" alt="KDE"/>
                                  </xsl:when>
								<xsl:when test="@category='gentoo'">
                                  <img src="/images/icon-gentoo.png" alt="gentoo"/>
                                </xsl:when>
                                <xsl:when test="@category='main'">
                                  <img src="/images/icon-stick.png" alt="stick man"/>
                                </xsl:when>
                                <xsl:when test="@category='ibm'">
                                  <img src="/images/icon-ibm.gif" alt="IBM"/>
                                </xsl:when>
                                <xsl:when test="@category='linux'">
                                  <img src="/images/icon-penguin.png" alt="Tux the Penguin"/>
                                </xsl:when>
                                <xsl:when test="@category='moo'">
                                  <img src="/images/icon-cow.png" alt="Larry the Cow"/>
                                </xsl:when>
                                <xsl:when test="@category='nvidia'">
                                  <img src="/images/icon-nvidia.png" alt="nvidia"/>
                                </xsl:when>
                              </xsl:choose>
                            </td>
                            <td valign="top">
                              <xsl:choose>
                                <xsl:when test="body">
                                  <xsl:apply-templates select="body"/>
                                </xsl:when>
                                <xsl:when test="section">
                                  <xsl:apply-templates select="section"/>
                                </xsl:when>
                              </xsl:choose>
                            </td>
                          </tr>
                        </table>
                      </xsl:when>
					  <xsl:when test="/email">
							<xsl:apply-templates select="/email/body"/>
					  </xsl:when>
                      <xsl:otherwise>
                        <br/>
                        <table border="0" class="content">
                          <tr>
                            <td>
                              <xsl:apply-templates select="chapter"/>
                            </td>
                          </tr>
                        </table>
                        <br/>
                        <br/>
                        <br/>
                      </xsl:otherwise>
                    </xsl:choose>
<!--content end-->
                  </td>
                </tr>
              </table>
            </td>
            <td width="1%" bgcolor="#dddaec" valign="top">
              <table border="0" cellspacing="5" cellpadding="0">
                <tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr>
					<xsl:choose>
					<xsl:when test="/mainpage/date">
                  		<tr><td align="center" class="alttext">
						Updated <xsl:value-of select="/mainpage/date"/>
						</td></tr>
						<tr>
						<td>
							<img src="/images/line.gif" alt="line"/>
						</td>
						</tr>
					</xsl:when>
					<xsl:when test="/news/date">
                  		<tr><td align="center" class="alttext">
						Updated <xsl:value-of select="/news/date"/>
						</td></tr>
						<tr>
						<td>
							<img src="/images/line.gif" alt="line"/>
						</td>
						</tr>
					</xsl:when>
					</xsl:choose>
			   	<tr>
                  <td align="center">
<!-- Begin PayPal Logo -->
					<p class="alttext"><b>Donate</b> to support our development efforts.</p>
                    <form action="https://www.paypal.com/cgi-bin/webscr" method="post">
                      <input type="hidden" name="cmd" value="_xclick"/>
                      <input type="hidden" name="business" value="drobbins@gentoo.org"/>
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
                <tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr>
			<tr>
			<td align="center">
				<a href="http://www.cafeshops.com/cp/store.aspx?s=gentoolinux">
				<img src="/images/store.png" alt="The Gentoo Linux Store" border="0"/>
				</a>
			</td>
		</tr>
		<tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr><tr>
                  <td align="center">
                    <p class="alttext">Win4Lin from <b>NeTraverse</b> lets you run Windows applications under Gentoo Linux at native speeds.</p>
		    <a href="http://www.netraverse.com/gentoo.htm" target="_top">
                      <img src="/images/netraverse-gentoo.gif" width="125" height="102" alt="Win4Lin at NeTraverse" border="0"/>
                    </a>
                     <p class="alttext"><a href="http://www.netraverse.com/gentoo.htm">Purchase Win4Lin "Gentoo Edition"</a> and you'll also get a special Gentoo discount. Every sale also helps support Gentoo Linux development :)</p>
                  </td>
		</tr>
		<tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr>
				<tr>
                  <td align="center">
                    <a href="http://www.qksrv.net/click-477620-5032687" target="_top">
                      <img src="http://www.qksrv.net/image-477620-5032687" width="125" height="125" alt="DDR Memory at Crucial.com" border="0"/>
                    </a>
                    <p class="alttext">Purchase RAM from <b>Crucial.com</b> and a percentage of your sale will go towards further Gentoo Linux development.</p>
                  </td>
                </tr>
                <tr>
                  <td>
                    <img src="/images/line.gif" alt="line"/>
                  </td>
                </tr>
</table>
            </td>
          </tr>
          <tr>
            <td align="right" class="infohead" width="100%" colspan="3" bgcolor="#7a5ada">
			Copyright 2001-2003 Gentoo
		Technologies, Inc.  Questions, Comments, Corrections?  Email <a class="highlight" href="mailto:www@gentoo.org">www@gentoo.org</a>.
			</td>
          </tr>
        </table>
      </body>
    </html>
  </xsl:template>
  <xsl:template match="newsitems">
    <xsl:apply-templates select="news"/>
  </xsl:template>
  <xsl:template match="news">
    <table width="100%" border="0" cellspacing="5" cellpadding="0">
      <tr>
        <td colspan="2" class="ncontent" bgcolor="#bbffbb">
          <p class="note">
            <font color="#7a5ada">
              <b>
                <xsl:value-of select="title"/>
              </b>
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
            <td class="alttext">
              <font color="#808080">Posted by <xsl:value-of select="poster"/> on <xsl:value-of select="date"/></font>
            </td>
          </xsl:when>
          <xsl:otherwise>
            <td class="alttext">
              <font color="#808080">Posted by <xsl:value-of select="poster"/> on <xsl:value-of select="date"/></font>
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
  
  <xsl:template match="body">
    <xsl:param name="chid"/>
    <xsl:apply-templates>
      <xsl:with-param name="chid" select="$chid"/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match="c">
    <span class="code">
      <xsl:apply-templates/>
    </span>
  </xsl:template>
  <xsl:template match="box">
    <p class="infotext">
      <xsl:apply-templates/>
    </p>
  </xsl:template>
  
  <xsl:template match="pre">
    <xsl:param name="chid"/>
    <xsl:variable name="prenum">
      <xsl:number level="any" from="chapter" count="pre"/>
    </xsl:variable>
    <xsl:variable name="preid">doc_chap<xsl:value-of select="$chid"/>_pre<xsl:value-of select="$prenum"/></xsl:variable>
    <a name="{$preid}"/>
    <table class="ntable" width="100%" cellspacing="0" cellpadding="0" border="0">
      <tr>
        <td class="infohead" bgcolor="#7a5ada">
          <p class="caption">
            <xsl:choose>
              <xsl:when test="@caption">
			Code listing <xsl:value-of select="$chid"/>.<xsl:value-of select="$prenum"/>: <xsl:value-of select="@caption"/>
		</xsl:when>
              <xsl:otherwise>
			Code listing <xsl:value-of select="$chid"/>.<xsl:value-of select="$prenum"/>
		</xsl:otherwise>
            </xsl:choose>
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
  <xsl:template match="path">
    <span class="path">
      <xsl:value-of select="."/>
    </span>
  </xsl:template>
  <xsl:template match="uri">
<!-- expand templates to handle things like <uri link="http://bar"><c>foo</c></uri> -->
    <xsl:choose>
      <xsl:when test="@link">
        <a href="{@link}">
          <xsl:apply-templates/>
        </a>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="loc" select="."/>
        <a href="{$loc}">
          <xsl:apply-templates/>
        </a>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
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
  <xsl:template match="e">
    <span class="emphasis">
      <xsl:apply-templates/>
    </span>
  </xsl:template>
  <xsl:template match="mail">
    <a href="mailto:{@link}">
      <xsl:value-of select="."/>
    </a>
  </xsl:template>
  <xsl:template match="table">
    <table class="ntable">
      <xsl:apply-templates/>
    </table>
  </xsl:template>
  <xsl:template match="tr">
    <tr>
      <xsl:apply-templates/>
    </tr>
  </xsl:template>
  <xsl:template match="ti">
    <td bgcolor="#ddddff" class="tableinfo">
      <xsl:apply-templates/>
    </td>
  </xsl:template>
  <xsl:template match="th">
    <td bgcolor="#7a5ada" class="infohead">
      <b>
        <xsl:apply-templates/>
      </b>
    </td>
  </xsl:template>
  <xsl:template match="ul">
    <ul>
      <xsl:apply-templates/>
    </ul>
  </xsl:template>
  <xsl:template match="ol">
    <ol>
      <xsl:apply-templates/>
    </ol>
  </xsl:template>
  <xsl:template match="li">
    <li>
      <xsl:apply-templates/>
    </li>
  </xsl:template>
    <xsl:template match="ignoreinemail">
        <xsl:apply-templates/>
	  </xsl:template>
	    <xsl:template match="ignoreinguide">
	      </xsl:template>

</xsl:stylesheet>
