function webMercatorToGeographic_simple( x, y )
{
    var radius = 6378137;
    var num3 = x / radius;
    var num4 = num3 * 57.295779513082323;
    var num5 = Math.floor((num4 + 180.0) / 360.0);
    var num6 = num4 - (num5 * 360.0);
    var num7 = 1.5707963267948966 - (2.0 * Math.atan(Math.exp((-1.0 * y) / 6378137.0)));
    var lat = num7 * 57.295779513082323;
    var lon = num6;
    return { x: lon, y: lat }

}

function geographicToWebMercator_simple( lon,  lat)
{
    var Radians_Per_Degrees = Math.PI / 180;
    var radius = 6378137;
    var x = lon * Radians_Per_Degrees * radius;
    var loc1 = lat * Radians_Per_Degrees;
    var loc2 = Math.sin(loc1);
    var y = radius * 0.5 * Math.log((1 + loc2) / (1 - loc2));
    return { x: x, y: y }

}
