<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output encoding="UTF-8" method="xml" indent="no" doctype-system="/dtd/project.dtd"/>
<xsl:template match="/staffingNeeds">
<project>
  <name>Требуются сотрудники</name>
  <longname>Gentoo Linux требуются сотрудники</longname>

  <date>автоматически</date><!-- Should give: Updated automatically -->
  <author title="сценарий"><mail link="devrel@gentoo.org">проект взаимодействия с разработчиками Gentoo</mail></author>

  <description>
    На этой странице перечислены заявки на разработчиков Gentoo, полученные рекрутерами Gentoo.
  </description>
  <longdescription>
    На этой странице перечисляются области, в которых Gentoo занят активным
    расширением разработки. Места открыты как для существующих разработчиков
    Gentoo, так и для тех, кто хочет стать разработчиком Gentoo. Список
    отсортирован по приоритету, от наибольшего к наименьшему.
  </longdescription>
  <extrachapter position="bottom">
    <title>Gentoo Linux требуются сотрудники</title>
    <section>
    <body>
      <p>
        На этой странице перечислены не все области, где приветствуется
        вклад новых участников, а лишь те, где разработчики нужны больше всего.
        Если вам интересно помочь в другой области, не стесняясь,
        напрямую свяжитесь с соответствующей группой разработчиков.
      </p>
      <p>
        Если вы заинтересованы помочь в проекте документации Gentoo (Gentoo
        Documentation Project), пожалуйста, ознакомьтесь с запросами,
        требующими внимания, в 
        <uri link="/proj/en/gdp/roadmap.xml">генплане GDP (англ.)</uri>.
      </p>
      <p>
        Если вы хотите принять участие в любой из следующих задач, пожалуйста,
        свяжитесь с <mail link="recruiters@gentoo.org">Gentoo Recruiters</mail>,
        направив копию своей заявки контактному лицу, указанному в списке.
      </p>
      <!-- Warn Russian reader that English use is mandatory -->
      <impo>
        Вся разработка и переписка по проектам Gentoo, кроме команд локализации,
        ведется только на английском языке! <e>- прим. пер.</e>
      </impo>
      <table>
        <tr>
          <th>Приоритет</th>
          <th>Тема</th>
          <th>Описание</th>
        </tr>
        <xsl:for-each select="needed">
          <!-- Key by priority; then alphabetically...
         No @priority is treated lowest, so this works as we need it to. -->
          <xsl:sort select="summary/@priority" order="ascending"/>
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
              Открыта
              <xsl:value-of select="summary/@dateRequested"/>
              <xsl:choose>
                <xsl:when test="contact/@herd != ''"></xsl:when>
                <xsl:when test="contact/@team != ''"></xsl:when>
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
  </extrachapter>
</project>
</xsl:template>
</xsl:stylesheet>
