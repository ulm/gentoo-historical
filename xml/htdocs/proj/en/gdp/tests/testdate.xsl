<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:func="http://exslt.org/functions" extension-element-prefixes="func" >

<xsl:output encoding="UTF-8" method="xml" indent="yes" doctype-system="/dtd/guide.dtd"/>

<func:function name="func:format-date">
  <xsl:param name="datum" />
  <xsl:param name="lingua" select="//*[1]/@lang"/>

  <xsl:variable name="mensis" select="document('months.xml')"/>

  <xsl:choose>
    <xsl:when test="string-length($datum)=10 and substring($datum,5,1)='-' and substring($datum,8,1)='-' and contains('|01|02|03|04|05|06|07|08|09|10|11|12|',concat('|',substring($datum,6,2),'|'))">
      <xsl:variable name="Y"><xsl:value-of select="number(substring($datum,1,4))"/></xsl:variable>
      <xsl:variable name="M"><xsl:value-of select="number(substring($datum,6,2))"/></xsl:variable>
      <xsl:variable name="D"><xsl:value-of select="number(substring($datum,9,2))"/></xsl:variable>
      <xsl:choose>
        <!-- Formatting per language happens here -->

        <!-- For complex and/or repeated cases, better use a dedicated function -->

        <!-- English -->
        <xsl:when test="$lingua='en'">
          <func:result select="func:format-date-en($mensis, $Y, $M, $D)"/>
        </xsl:when>

        <!-- Danish / German / Finnish -->
        <xsl:when test="$lingua='da' or $lingua='de' or $lingua='fi'">
          <func:result select="concat($D, '. ', $mensis//months[@lang=$lingua]/month[position()=$M], ' ', $Y)"/>
        </xsl:when>

        <!-- Spanish -->
        <xsl:when test="$lingua='es'">
          <func:result select="concat($D, ' de ', $mensis//months[@lang=$lingua]/month[position()=$M], ', ', $Y)"/>
        </xsl:when>
        
        <!-- Brazilain Portuguese -->
        <xsl:when test="$lingua='pt_br'">
          <func:result select="concat($D, ' de ', $mensis//months[@lang=$lingua]/month[position()=$M], ' de ', $Y)"/>
        </xsl:when>
        
        <!-- Hungarian -->
        <xsl:when test="$lingua='hu'">
          <func:result select="concat($Y, '. ', $mensis//months[@lang=$lingua]/month[position()=$M], ' ', $D, '.')"/>
        </xsl:when>

        <!-- Japanese -->
        <xsl:when test="$lingua='ja'">
          <func:result select="concat($Y, '年 ', $M, '月 ', $D, '日 ')"/>
        </xsl:when>

        <!-- Chinese -->
        <xsl:when test="$lingua='zh_cn' or $lingua='zh_tw'">
          <func:result select="concat($Y, '年 ', $M, '月 ', $D, '號 ')"/>
        </xsl:when>

        <!-- Korean -->
        <xsl:when test="$lingua='ko'">
          <func:result select="concat($Y, '년 ', $M, '월 ', $D, '일')"/>
        </xsl:when>

        <!-- French -->
        <xsl:when test="$lingua='fr'">
          <func:result select="func:format-date-fr($mensis, $Y, $M, $D)" />
        </xsl:when>

        <!-- Dutch / Greek / Indonesian / Italian / Polish / Romanian / Russian / Swedish / Turkish -->
        <xsl:when test="$lingua='nl' or $lingua='el' or $lingua='id' or $lingua='it' or $lingua='pl' or $lingua='ro' or $lingua='ru' or $lingua='sv' or $lingua='tr'">
          <func:result select="concat($D, ' ', $mensis//months[@lang=$lingua]/month[position()=$M], ' ', $Y)"/>
        </xsl:when>

        <xsl:otherwise> <!-- Default to English -->
          <func:result select="func:format-date-en($mensis, $Y, $M, $D)" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:when>
    <xsl:otherwise>
      <func:result select="$datum" />
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!-- Format date in  ENGLISH -->
<func:function name="func:format-date-en">
  <xsl:param name="mensis" />
  <xsl:param name="Y" />
  <xsl:param name="M" />
  <xsl:param name="D" />
  <func:result select="concat($mensis//months[@lang='en']/month[position()=$M], ' ', $D, ', ', $Y)" />
</func:function>

<!-- Format date in  FRENCH -->
<func:function name="func:format-date-fr">
  <xsl:param name="mensis" />
  <xsl:param name="Y" />
  <xsl:param name="M" />
  <xsl:param name="D" />
  <func:result>
    <xsl:value-of select="$D"/>
    <xsl:if test="$D=1">er</xsl:if>
    <xsl:value-of select="concat(' ', $mensis//months[@lang='fr']/month[position()=$M], ' ', $Y)"/>
  </func:result>
</func:function>

<xsl:param name="date">1967-06-05</xsl:param>
<!-- Start outputting data -->
<xsl:template match="/doc">

<guide link="testdate.xml">
<title>Test Date Formatting</title>

<author title="Author">
  <mail link="neysx@gentoo.org">Xavier Neys</mail>
</author>

<abstract>
This page shows how dates could be formatted for each language
</abstract>

<license/>

<version>1.0</version>
<date>November 13, 2004</date>

<chapter>
<title>Introduction</title>
<section>
<title>Some information</title>
<body>

<p>
At the moment, we can't process the date elements easily to do some
comparisons, sorting... because it is written in plain English and in many
different languages.
</p>

<p>
Besides, some people have been very creative and dates are formatted in many
different ways in English and in many translations.
</p>

<p>
XSLT 2.0 has some date formatting routines but XSLT 1.0 hasn't and it seems
like we'll have to do with it for quite a while.
</p>

<p>
Fortunately, we do not need any advanced date checking and validating library.
All we need is to be able to display YYYY-MM-DD in a limited set of languages.
</p>

<p>
The table below shows different examples of dates formatted for different
languages.  Illegal dates are shown on purpose. I'll include validation later
on but I don't need your feedback for that.
</p>

<p>
The <c>&lt;date&gt;</c> element in our documentation would be expected to be
formatted as <path>YYYY-MM-DD</path> so that it can be easily used in automatic
processing. If a date does not match that pattern, it would be copied verbatim
for backwards compatibility. Otherwise, it is formatted for the given language
which defaults to the lang attribute of the root element. The default language
is English of course.
</p>

</body>
</section>
<section>
<title>I need your feedback</title>
<body>

<p>
The dates below have been formatted based on my limited knowledge of dates in
plenty of languages and on how they currently appear in the docs. Some guesses
are probably right, some less because of the many different formats currently
used.
</p>

<p>
Please check the dates below in your language and let me know if they look good
or what needs to be fixed. Most Asian docs use Arabic digits but some don't.
Please let me know what is best.
</p>

<p>
Check whether month names should be capitalized. I know they should in English
and they must not in French. I noticed some languages used capitalization but
the output of <c>date</c> differs. Please check and let me know.
</p>

</body>
</section>
</chapter>

<chapter>
<title>The Dates</title>
<section>
<body>

<p>
You can try with your own values by appending a date parameter to the url like
this <uri>?date=2004-12-25#doc_chap2</uri>. The date will be displayed in the
first column.
</p>

<table>
<tr>
 <ti>Lang&#160;\&#160;Date</ti>
 <th><xsl:value-of select="$date" /></th>
 <xsl:for-each select="//doc/date"><xsl:sort select="."/><th><xsl:value-of select="." /></th></xsl:for-each>
</tr>
    <xsl:apply-templates select="lang/code">
     <xsl:sort select="."/>
    </xsl:apply-templates>
</table>
</body>
</section>
</chapter>
</guide>
</xsl:template>

  <xsl:template match="code">
    <xsl:variable name="LL" select="."/>
    <tr>
     <th><xsl:value-of select="$LL" /></th>
     <ti><xsl:value-of select="func:format-date($date,$LL)" /></ti>
     <xsl:for-each select="//doc/date"><xsl:sort select="."/><ti><xsl:value-of select="func:format-date(.,$LL)" /></ti></xsl:for-each>
    </tr>
  </xsl:template>

</xsl:stylesheet>
