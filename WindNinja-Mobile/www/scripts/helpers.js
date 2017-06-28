// Convert px to em and vice-versa
$.fn.toEm = function (settings) {
	settings = jQuery.extend({
		scope: 'body'
	}, settings);
	var that = parseInt(this[0], 10),
		scopeTest = jQuery('<div style="display: none; font-size: 1em; margin: 0; padding:0; height: auto; line-height: 1; border:0;">&nbsp;</div>').appendTo(settings.scope),
		scopeVal = scopeTest.height();
	scopeTest.remove();
	return (that / scopeVal).toFixed(8);
};
$.fn.toPx = function (settings) {
	settings = jQuery.extend({
		scope: 'body'
	}, settings);
	var that = parseFloat(this[0]),
		scopeTest = jQuery('<div style="display: none; font-size: 1em; margin: 0; padding:0; height: auto; line-height: 1; border:0;">&nbsp;</div>').appendTo(settings.scope),
		scopeVal = scopeTest.height();
	scopeTest.remove();
	return Math.round(that * scopeVal);
};
// Convert Degrees to Radians and vice-versa
Number.prototype.toRad = function () {
	return this * Math.PI / 180;
};
Number.prototype.toDeg = function () {
	return this * 180 / Math.PI;
};
String.prototype.toTitleCase = function () {
	return this.replace(/\w\S*/g, function (txt) { return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase(); });
};
String.prototype.padLeft = function (len) {
	var s = new String(this);
	if (this.length < len) {
		for (var i = 0; i < len - this.length; ++i) {
			s = '0'.charAt(0).concat(s);
		}
	}

	return s;
};
if (!String.prototype.format) {
	String.prototype.format = function () {
		var args = arguments;
		return this.replace(/{(\d+)}/g, function (match, number) {
			return typeof args[number] != 'undefined'
			  ? args[number]
			  : match
			;
		});
	};
}

$.fn.spin.presets.windninja = {
	lines: 9, // The number of lines to draw
	length: 10, // The length of each line
	width: 5, // The line thickness
	radius: 10, // The radius of the inner circle
	corners: 1, // Corner roundness (0..1)
	rotate: 0, // The rotation offset
	direction: 1, // 1: clockwise, -1: counterclockwise
	color: '#000', // #rgb or #rrggbb or array of colors
	speed: 1, // Rounds per second
	trail: 60, // Afterglow percentage
	shadow: true, // Whether to render a shadow
	hwaccel: true, // Whether to use hardware acceleration
	className: 'spinner', // The CSS class to assign to the spinner
	zIndex: 2e9, // The z-index (defaults to 2000000000)
	top: '50%', // Top position relative to parent
	left: '50%' // Left position relative to parent
};