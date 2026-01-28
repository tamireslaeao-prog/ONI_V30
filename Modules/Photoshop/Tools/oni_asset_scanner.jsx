/*
 * ONI ASSET SCANNER (PhD Edition)
 * Scans Photoshop Application Presets and Directories to build the Master Catalog.
 * V2 - With JSON Polyfill
 */

#target photoshop

// ============ JSON POLYFILL ============
if (typeof JSON !== 'object') { JSON = {}; }
(function () {
    'use strict';
    function f(n) { return n < 10 ? '0' + n : n; }
    if (typeof Date.prototype.toJSON !== 'function') {
        Date.prototype.toJSON = function () { return isFinite(this.valueOf()) ? this.getUTCFullYear() + '-' + f(this.getUTCMonth() + 1) + '-' + f(this.getUTCDate()) + 'T' + f(this.getUTCHours()) + ':' + f(this.getUTCMinutes()) + ':' + f(this.getUTCSeconds()) + 'Z' : null; };
    }
    var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        meta = { '\b': '\\b', '\t': '\\t', '\n': '\\n', '\f': '\\f', '\r': '\\r', '"': '\\"', '\\': '\\\\' };
    function quote(string) { escapable.lastIndex = 0; return escapable.test(string) ? '"' + string.replace(escapable, function (a) { var c = meta[a]; return typeof c === 'string' ? c : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4); }) + '"' : '"' + string + '"'; }
    function str(key, holder) {
        var i, k, v, length, partial, value = holder[key];
        if (value && typeof value === 'object' && typeof value.toJSON === 'function') { value = value.toJSON(key); }
        switch (typeof value) {
            case 'string': return quote(value);
            case 'number': return isFinite(value) ? String(value) : 'null';
            case 'boolean': case 'null': return String(value);
            case 'object': if (!value) return 'null'; partial = []; if (Object.prototype.toString.apply(value) === '[object Array]') { length = value.length; for (i = 0; i < length; i += 1) { partial[i] = str(i, value) || 'null'; } v = partial.length === 0 ? '[]' : '[' + partial.join(',') + ']'; return v; } for (k in value) { if (Object.prototype.hasOwnProperty.call(value, k)) { v = str(k, value); if (v) { partial.push(quote(k) + ':' + v); } } } v = partial.length === 0 ? '{}' : '{' + partial.join(',') + '}'; return v;
        }
    }
    if (typeof JSON.stringify !== 'function') { JSON.stringify = function (value) { return str('', { '': value }); }; }
}());

var catalog = {
    brushes: [],
    styles: [],
    actions: [],
    scripts: []
};

function scanDir(path, ext) {
    var folder = new Folder(path);
    if (!folder.exists) return [];
    var files = folder.getFiles("*." + ext);
    var names = [];
    for (var i = 0; i < files.length; i++) {
        names.push(files[i].name);
    }
    return names;
}

// 1. Scan Application Presets
var appPath = app.path;
catalog.brushes = scanDir(appPath + "/Presets/Brushes", "abr");
catalog.styles = scanDir(appPath + "/Presets/Styles", "asl");
catalog.scripts = scanDir(appPath + "/Presets/Scripts", "jsx");

// 2. Scan Actions (via ActionManager - limited, listing sets)
// Note: AM cannot list actions easily without iterating blindly. 
// We will list the Scripts folder instead as a proxy for automation capability.

// Output to relative path (Up 2 levels to ONI_V30, then /temp)
var scriptFile = new File($.fileName);
var rootDir = scriptFile.parent.parent.parent; // Tools -> Photoshop -> Modules -> ONI_V30
var tempDir = new Folder(rootDir + "/temp");
if (!tempDir.exists) tempDir.create();

var jsonOut = new File(tempDir + "/ONI_ASSET_CATALOG.json");
jsonOut.open("w");
jsonOut.write(JSON.stringify(catalog, null, 2));
jsonOut.close();

alert("Asset Catalog Saved to: " + jsonOut.fsName + "\nBrushes: " + catalog.brushes.length + "\nStyles: " + catalog.styles.length);
