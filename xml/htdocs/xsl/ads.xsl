<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:template name="ads">
 <xsl:param name="images"/>

  <!-- OSL -->
    <tr lang="en">
    <td align="center" class="topsep">
            <a href="http://osuosl.org/contribute">
      <img src="{concat($images,'images/osuosl.png')}" width="125" height="50" alt="Support OSL" title="Support OSL" border="0"/>
        </a>
    </td>
    </tr>
  <!-- /OSL -->

  <!-- VR -->
    <tr lang="en">
    <td align="center" class="topsep">
            <a href="http://www.vr.org">
      <img src="{concat($images,'images/vr-ad.png')}" width="125" height="144" alt="Gentoo Centric Hosting: vr.org" title="Gentoo Centric Hosting: vr.org" border="0"/>
        </a>
    </td>
    </tr>
  <!-- /VR -->

  <!-- Tek -->
    <tr lang="en">
      <td align="center" class="topsep">
      <a href="http://www.tek.net" target="_top">
        <img src="{concat($images,'images/tek-gentoo.gif')}" width="125" height="125" alt="Tek Alchemy" title="Tek Alchemy" border="0"/>
      </a>
      </td>
    </tr>
  <!-- /Tek -->

  <!-- SevenL -->
    <tr lang="en">
    <td align="center" class="topsep">
      <a href="http://www.sevenl.net" target="_top">
        <img src="{concat($images,'images/sponsors/sevenl_ad.png')}" width="125" height="144" alt="SevenL.net" title="SevenL.net" border="0"/>
      </a>
    </td>
    </tr>
  <!-- /SevenL -->

  <!-- GNi -->
    <tr lang="en">
    <td align="center" class="topsep">
        <a href="http://www.gni.com" target="_top">
          <img src="{concat($images,'images/gni_logo.png')}" width="125" alt="Global Netoptex Inc." title="Global Netoptex Inc." border="0"/>
      </a>
    </td>
    </tr>
  <!-- /GNi -->

  <!-- bytemark -->
    <tr lang="en">
    <td align="center" class="topsep">
        <a href="http://www.bytemark.co.uk/r/gentoo-home" target="_top">
          <img src="{concat($images,'images/sponsors/bytemark_ad.png')}" width="125" alt="Bytemark" title="Bytemark" border="0"/>
      </a>
    </td>
    </tr>
  <!-- /bytemark -->
  
  <!-- kredit -->
    <tr lang="en">
    <td align="center" class="topsep">
		<a href="http://www.online-kredit-index.de/" target="_top">
          <img src="{concat($images,'images/sponsors/kredit-ad.jpg')}" width="125" alt="Online Kredit Index" title="Online Kredit Index" border="0"/>
      </a>
    </td>
    </tr>
  <!-- /kredit -->
</xsl:template>

</xsl:stylesheet>
