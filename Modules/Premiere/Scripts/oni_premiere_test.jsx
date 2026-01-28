
// ONI Premiere Test Script
// Simple smoke test to verify connectivity

try {
    alert("ONI SYSTEM: Premiere Pro Connection Verified!");

    // Log to console if available
    if (typeof console !== 'undefined') {
        console.log("ONI: Premiere Bridge Active");
    }
} catch (e) {
    // If alert fails (headless mode?), try writing to file?
    // For now, we assume UI context
}
