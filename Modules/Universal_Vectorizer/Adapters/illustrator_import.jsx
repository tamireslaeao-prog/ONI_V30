
/*
    ONI Illustrator Adapter - Universal SVG Open
*/

function openUniversalSVG(svgPath) {
    var fileRef = new File(svgPath);

    if (!fileRef.exists) {
        alert("ONI Error: SVG file not found at " + svgPath);
        return;
    }

    try {
        app.open(fileRef);
    } catch (e) {
        alert("ONI Open Failed: " + e);
    }
}

if (typeof oni_svg_path !== 'undefined') {
    openUniversalSVG(oni_svg_path);
}
