<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output encoding="iso-8859-15" method="html" indent="yes" doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"/>
	<xsl:preserve-space elements="pre"/>
	<xsl:template match="img">
		<img src="{@src}"/>
	</xsl:template>
	<xsl:template match="/guide">
	<html>
	<head>
<link title="new" rel="stylesheet" href="/css/main.css" type="text/css"/>
	<title>Printable Linux <xsl:choose><xsl:when test="/guide/@type='project'">Projects</xsl:when><xsl:otherwise>Documentation</xsl:otherwise></xsl:choose>
-- 
	<xsl:choose><xsl:when test="subtitle"><xsl:value-of select="title"/>: <xsl:value-of select="subtitle"/></xsl:when><xsl:otherwise><xsl:value-of select="title"/></xsl:otherwise></xsl:choose></title>
	</head>
	<body style="margin-left:0px;margin-top:0px;" bgcolor="#ffffff">
			<table border="0" cellspacing="0" cellpadding="0" width="100%">
				<tr>
					<td width="99%" class="content" valign="top" align="left">
						
						<p class="dochead">
                      <xsl:choose>
                        <xsl:when test="/guide/subtitle"><xsl:value-of select="/guide/title"/>: <xsl:value-of select="/guide/subtitle"/></xsl:when>
                        <xsl:otherwise>
                          <xsl:value-of select="/guide/title"/>
                        </xsl:otherwise>
                      </xsl:choose>
                    </p>
		<p><xsl:apply-templates select="author"/>
		<em>Updated <xsl:value-of select="/guide/date"/></em></p>

                    <xsl:apply-templates select="chapter"/>
                    <br/>
                    <xsl:if test="/guide/license">
                        <xsl:apply-templates select="license"/>
                    </xsl:if>
                    <br/>
<!--content end-->
                  </td>
			</tr>
			</table>
	  </body>
    </html>
  </xsl:template>
  <xsl:template match="mail">
    <a href="mailto:{@link}">
      <xsl:value-of select="."/>
    </a>
  </xsl:template>
  <xsl:template match="author/mail">
    <b>
      <a class="altlink" href="mailto:{@link}">
        <xsl:value-of select="."/>
      </a>
    </b>
  </xsl:template>
  <xsl:template match="author">
    <xsl:apply-templates/>
    <xsl:if test="@title">
      <br/>
      <i>
        <xsl:value-of select="@title"/>
      </i>
    </xsl:if>
    <br/>
    <br/>
  </xsl:template>
  <xsl:template match="chapter">
    <xsl:variable name="chid"><xsl:number/></xsl:variable>
    <xsl:choose>
      <xsl:when test="title">
        <p class="chaphead">
          <font class="chapnum">
            <a name="doc_chap{$chid}"><xsl:number/>.</a>
          </font>
          <xsl:value-of select="title"/>
        </p>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test="/guide">
          <p class="chaphead">
            <font class="chapnum">
              <a name="doc_chap{$chid}"><xsl:number/>.</a>
            </font>
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
  <xsl:template match="section">
    <xsl:param name="chid"/>
    <xsl:if test="title">
      <xsl:variable name="sectid">doc_chap<xsl:value-of select="$chid"/>_sect<xsl:number/></xsl:variable>
      <p class="secthead">
        <a name="{$sectid}"><xsl:value-of select="title"/>&#160;</a>
      </p>
    </xsl:if>
    <xsl:apply-templates select="body">
      <xsl:with-param name="chid" select="$chid"/>
    </xsl:apply-templates>
  </xsl:template>
<!--  
  <xsl:template match="subsection">
    <xsl:param name="chapid"/>
    <xsl:if test="title">
      <xsl:variable name="subsectid"><xsl:value-of select="$chapid"/>_subsect<xsl:number/></xsl:variable>
      <p class="subsecthead">
        <a name="{$subsectid}"><xsl:value-of select="title"/>&#160;</a>
      </p>
    </xsl:if>
    <xsl:apply-templates select="body"/>
  </xsl:template>
-->
  <xsl:template match="figure">
    <xsl:with-param name="chid"/>
    <xsl:variable name="fignum">
      <xsl:number level="any" from="chapter" count="figure"/>
    </xsl:variable>
    <xsl:variable name="figid">doc_chap<xsl:value-of select="$chid"/>_fig<xsl:value-of select="$fignum"/></xsl:variable>
    <br/>
    <a name="{$figid}"/>
    <table cellspacing="0" cellpadding="0" border="0">
      <tr>
        <td class="infohead" bgcolor="#7a5ada">
          <p class="caption">
            <xsl:choose>
              <xsl:when test="@caption">
				Figure <xsl:value-of select="$chid"/>.<xsl:value-of select="$fignum"/>: <xsl:value-of select="@caption"/>
			</xsl:when>
              <xsl:otherwise>
				Figure <xsl:value-of select="$chid"/>.<xsl:value-of select="$fignum"/>
			</xsl:otherwise>
            </xsl:choose>
          </p>
        </td>
      </tr>
      <tr>
        <td align="center" bgcolor="#ddddff">
          <xsl:choose>
            <xsl:when test="@short">
              <img src="{@link}" alt="Fig. {$fignum}: {@short}"/>
            </xsl:when>
            <xsl:otherwise>
              <img src="{@link}" alt="Fig. {$fignum}"/>
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
          <a href="{@linkto}">
            <img src="{@link}" alt="{@short}"/>
          </a>
        </xsl:when>
        <xsl:otherwise>
          <img src="{@link}" alt="{@short}"/>
        </xsl:otherwise>
      </xsl:choose>
    </center>
  </xsl:template>
  <xsl:template match="br">
    <br/>
  </xsl:template>
  <xsl:template match="note">
    <table class="ncontent" width="100%" border="0" cellspacing="0" cellpadding="0">
      <tr>
        <td bgcolor="#bbffbb">
          <p class="note">
            <b>Note: </b>
            <xsl:apply-templates/>
          </p>
        </td>
      </tr>
    </table>
  </xsl:template>
  <xsl:template match="impo">
    <table class="ncontent" width="100%" border="0" cellspacing="0" cellpadding="0">
      <tr>
        <td bgcolor="#ffffbb">
          <p class="note">
            <b>Important: </b>
            <xsl:apply-templates/>
          </p>
        </td>
      </tr>
    </table>
  </xsl:template>
  <xsl:template match="warn">
    <table class="ncontent" width="100%" border="0" cellspacing="0" cellpadding="0">
      <tr>
        <td bgcolor="#ffbbbb">
          <p class="note">
            <b>Warning: </b>
            <xsl:apply-templates/>
          </p>
        </td>
      </tr>
    </table>
  </xsl:template>
  <xsl:template match="codenote">
    <font class="comment">// <xsl:value-of select="."/></font>
  </xsl:template>
  <xsl:template match="comment">
    <font class="comment">
      <xsl:apply-templates/>
    </font>
  </xsl:template>
  <xsl:template match="i">
    <font class="input">
      <xsl:apply-templates/>
    </font>
  </xsl:template>
  <xsl:template match="b">
    <b>
      <xsl:apply-templates/>
    </b>
  </xsl:template>
  <xsl:template match="brite">
    <font color="#ff0000">
      <b>
        <xsl:apply-templates/>
      </b>
    </font>
  </xsl:template>
  
  <xsl:template match="body">
    <xsl:param name="chid"/>
    <xsl:apply-templates>
      <xsl:with-param name="chid" select="$chid"/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template match="c">
    <font class="code">
      <xsl:apply-templates/>
    </font>
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
    <font class="path">
      <xsl:value-of select="."/>
    </font>
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
    <font class="emphasis">
      <xsl:apply-templates/>
    </font>
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
<xsl:template match="license">
<pre>
The contents of this document are licensed under the <a href="http://creativecommons.org/licenses/by-sa/1.0">Creative Commons - Attribution / Share Alike</a> license.
</pre>
</xsl:template>
</xsl:stylesheet>
