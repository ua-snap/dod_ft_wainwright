<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.2.0-Bonn" minScale="1e+8" maxScale="0">
  <pipe>
    <rasterrenderer alphaBand="-1" opacity="1" band="2" type="paletted">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry value="0" color="#ca0020" alpha="255" label="&lt;-45"/>
        <paletteEntry value="1" color="#e66e61" alpha="255" label="-30"/>
        <paletteEntry value="2" color="#f5c1a9" alpha="255" label="-15"/>
        <paletteEntry value="3" color="#f7f7f7" alpha="255" label="0"/>
        <paletteEntry value="4" color="#b4d6e7" alpha="255" label="15"/>
        <paletteEntry value="5" color="#63a9cf" alpha="255" label="30"/>
        <paletteEntry value="6" color="#0571b0" alpha="255" label=">60"/>
      </colorPalette>
      <colorramp name="[source]" type="gradient">
        <prop v="202,0,32,255" k="color1"/>
        <prop v="5,113,176,255" k="color2"/>
        <prop v="0" k="discrete"/>
        <prop v="gradient" k="rampType"/>
        <prop v="0.25;244,165,130,255:0.5;247,247,247,255:0.75;146,197,222,255" k="stops"/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation saturation="0" colorizeGreen="128" colorizeStrength="100" colorizeBlue="128" grayscaleMode="0" colorizeOn="0" colorizeRed="255"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
