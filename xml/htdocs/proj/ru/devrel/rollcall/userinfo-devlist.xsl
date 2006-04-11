<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mainpage SYSTEM "/dtd/guide.dtd">

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:exslt="http://exslt.org/common"
                extension-element-prefixes="exslt" >

<xsl:preserve-space elements="*"/>
<xsl:param name="statusFilter"/>

<xsl:variable name="devaway" select='document("/dyn/devaway/devaway.xml")'/>

<xsl:template match="/userlist">
  <mainpage id="about" lang="ru">
    <title>Разработчики Gentoo Linux</title>
    <author title="сформировано сценарием"><mail link="devrel@gentoo.org">Проект взаимодействия с разработчиками Gentoo</mail></author>

    <version>Текущая</version>
    <chapter>
    <section>
    <title>
      Список 
      <xsl:choose>
        <xsl:when test="$statusFilter = ''">действующих</xsl:when>
        <xsl:when test="$statusFilter = 'Retired'">отставных</xsl:when>
        <xsl:otherwise>'<xsl:value-of select="$statusFilter"/>'</xsl:otherwise>
      </xsl:choose>
      разработчиков Gentoo Linux
    </title>
    <body>
      <p>
        <xsl:choose>
          <xsl:when test="$statusFilter = ''">
            В следующей таблице приведен список действующих разработчиков
            Gentoo. Отставные разработчики перечислены на странице
            <uri link="userinfo.xml?statusFilter=Retired">отставных
            разработчиков Gentoo</uri>.
          </xsl:when>
          <xsl:when test="$statusFilter = 'Retired'">
            В следующей таблице приведен список отставных разработчиков Gentoo.
            Действующие разработчики перечислены на странице <uri
            link="userinfo.xml">разработчиков Gentoo</uri>.
          </xsl:when>
        </xsl:choose>
      </p>
        <xsl:if test="$statusFilter = ''">
          <p>
            С разработчиками можно связаться, направив сообщение по адресу
            псевдоним AT gentoo.org; многих разработчиков можно найти на
            IRC (freenode) на канале #gentoo или #gentoo-dev (требуется право
            голоса) под соответствующим псевдонимом.
          </p>
          <p>
            Перед тем, как пытаться с кем-то связаться, желательно убедиться,
            что его нет в списке <uri link="devaway.xml">отсутствующих
            разработчиков</uri>.
          </p>
      </xsl:if>
      <table>
      <tr>
        <th>Псевдоним</th>
        <th>Имя</th>
        <th>
          <xsl:if test="$statusFilter != 'Retired'">Ключ GPG</xsl:if>
          <xsl:if test="$statusFilter = 'Retired'">Состояние</xsl:if>
        </th>
        <th>Местонахождение</th>
        <th>Области ответственности</th>
      </tr>
      <xsl:for-each select="user">
        <xsl:sort select="@username"/>
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
              <xsl:choose>
                <xsl:when test="starts-with(pgpkey, '0x')">
                  <xsl:value-of select="translate(pgpkey,'abcdef','ABCDEF')"/>
                </xsl:when>
                <xsl:when test="string-length(pgpkey) = 8">
                  0x<xsl:value-of select="translate(pgpkey,'abcdef','ABCDEF')"/>
                </xsl:when>
                <xsl:when test="string-length(pgpkey) &gt; 0">
                  Неверный формат ключа!
                </xsl:when>
              </xsl:choose>
            </xsl:if>
            <xsl:if test="$statusFilter = 'Retired'">
              <xsl:if test="status and status != 'active'">
                <xsl:value-of select="concat(translate(substring(status, 1, 1 ),'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), substring(status, 2, string-length(status)))" />
              </xsl:if>
            </xsl:if>
          </ti>
          <ti>
            <xsl:if test="location"><xsl:value-of select="location"/></xsl:if>
            <xsl:if test="$devaway/devaway/dev[@nick=$username]">
              (<uri><xsl:attribute name="link"><xsl:value-of select="concat('devaway.xml?select=', $username,'#',$username)"/></xsl:attribute>away</uri>)
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
      </xsl:for-each>
    </table>
  </body>

</section>
</chapter>
</mainpage>
</xsl:template>
</xsl:stylesheet>
