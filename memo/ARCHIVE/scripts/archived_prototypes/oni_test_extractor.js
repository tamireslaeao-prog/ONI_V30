/**
 * ONI QUICK TEST - Teste Rápido de Extração
 * Use este script para testar se a extração está funcionando
 */

function cTID(s) { return app.charIDToTypeID(s); }

// Teste 1: JSON está disponível?
var test1 = (typeof JSON !== 'undefined' && typeof JSON.stringify === 'function');

// Teste 2: Documento aberto?
var test2 = (app.documents.length > 0);

// Teste 3: Layer ativa tem efeitos?
var test3 = false;
var effectsList = [];
if (test2) {
    try {
        var ref = new ActionReference();
        ref.putEnumerated(cTID("Lyr "), cTID("Ordn"), cTID("Trgt"));
        var desc = executeActionGet(ref);
        
        if (desc.hasKey(cTID("Lefx"))) {
            test3 = true;
            var lefx = desc.getObjectValue(cTID("Lefx"));
            
            // Detectar quais efeitos estão presentes
            if (lefx.hasKey(cTID('ebbl'))) effectsList.push("Bevel & Emboss");
            if (lefx.hasKey(cTID('GrOv'))) effectsList.push("Gradient Overlay");
            if (lefx.hasKey(cTID('ChFX'))) effectsList.push("Satin");
            if (lefx.hasKey(cTID('DrSh'))) effectsList.push("Drop Shadow");
            if (lefx.hasKey(cTID('IrSh'))) effectsList.push("Inner Shadow");
            if (lefx.hasKey(cTID('FrFX'))) effectsList.push("Stroke");
            if (lefx.hasKey(cTID('IrGl'))) effectsList.push("Inner Glow");
            if (lefx.hasKey(cTID('OrGl'))) effectsList.push("Outer Glow");
            if (lefx.hasKey(cTID('SoFi'))) effectsList.push("Color Overlay");
        }
    } catch(e) {}
}

// Teste 4: Pode escrever no Desktop?
var test4 = false;
try {
    var testFile = new File(Folder.desktop + "/ONI_TEST_WRITE.txt");
    testFile.open("w");
    testFile.write("TEST OK");
    testFile.close();
    testFile.remove();
    test4 = true;
} catch(e) {}

// Gerar relatório
var report = "═══════════════════════════════════════════\n";
report += "  ONI QUICK TEST - DIAGNOSTIC REPORT\n";
report += "═══════════════════════════════════════════\n\n";

report += "Test 1: JSON Support\n";
report += "Status: " + (test1 ? "✓ PASS" : "✗ FAIL") + "\n";
report += "Detail: " + (test1 ? "JSON.stringify available" : "JSON polyfill needed") + "\n\n";

report += "Test 2: Document Open\n";
report += "Status: " + (test2 ? "✓ PASS" : "✗ FAIL") + "\n";
if (test2) {
    report += "Document: " + app.activeDocument.name + "\n";
    report += "Active Layer: " + app.activeDocument.activeLayer.name + "\n";
} else {
    report += "Detail: No document open\n";
}
report += "\n";

report += "Test 3: Layer Has Effects\n";
report += "Status: " + (test3 ? "✓ PASS" : "✗ FAIL") + "\n";
if (test3) {
    report += "Effects Found: " + effectsList.length + "\n";
    for (var i = 0; i < effectsList.length; i++) {
        report += "  • " + effectsList[i] + "\n";
    }
} else {
    report += "Detail: Active layer has no Layer Styles\n";
}
report += "\n";

report += "Test 4: Desktop Write Access\n";
report += "Status: " + (test4 ? "✓ PASS" : "✗ FAIL") + "\n";
report += "Detail: " + (test4 ? "Can write to Desktop" : "Permission denied") + "\n\n";

report += "═══════════════════════════════════════════\n";
report += "OVERALL: ";
if (test1 && test2 && test3 && test4) {
    report += "✓ ALL TESTS PASSED - READY TO EXTRACT\n";
} else {
    report += "✗ SOME TESTS FAILED - CHECK DETAILS\n";
}
report += "═══════════════════════════════════════════\n\n";

// Recommendations
report += "RECOMMENDATIONS:\n";
if (!test1) report += "⚠ Install ONI Style Extractor V4 with JSON polyfill\n";
if (!test2) report += "⚠ Open a PSD document first\n";
if (!test3) report += "⚠ Select a layer with Layer Styles (fx icon visible)\n";
if (!test4) report += "⚠ Check Desktop permissions or folder access\n";

if (test1 && test2 && test3 && test4) {
    report += "✓ System ready! You can now run ONI Style Extractor V4\n";
}

// Salvar relatório
try {
    var reportFile = new File(Folder.desktop + "/ONI_DIAGNOSTIC_REPORT.txt");
    reportFile.encoding = "UTF-8";
    reportFile.open("w");
    reportFile.write(report);
    reportFile.close();
    
    alert("Diagnostic Complete!\n\nReport saved to:\nDesktop/ONI_DIAGNOSTIC_REPORT.txt\n\n" + 
          "Tests Passed: " + [test1, test2, test3, test4].filter(function(t){return t;}).length + "/4");
} catch(e) {
    alert(report);
}