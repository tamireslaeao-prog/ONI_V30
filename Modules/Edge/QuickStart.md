# 🌐 ONI EDGE CONTROL SYSTEM
> **Version:** 1.0  
> **Status:** PRODUCTION READY

---

## 🌟 OVERVIEW
Complete automation framework for Microsoft Edge browser with real-time monitoring, deep profile analysis, tab management, and web scraping capabilities via Chrome DevTools Protocol (CDP).

---

## 📂 SYSTEM ARCHITECTURE

```
C:\ONI\Edge\
├── oni_lib_edge.js              # Core JavaScript Library (CDP)
├── browser_db.json              # Harvested browser database
├── sentinel_log.txt             # Real-time activity log
├── Scripts\
│   ├── ONI_Edge_Harvester.ps1   # Deep profile scanner
│   ├── ONI_Edge_Sentinel.ps1    # Real-time monitor
│   ├── ONI_Edge_Launcher.ps1    # Advanced browser starter
│   └── ONI_Edge_Automation.ps1  # Bulk automation tasks
└── Profiles\
    ├── Default\                 # Default profile backup
    ├── Dev\                     # Development profile
    └── Test\                    # Testing profile
```

---

## 🔑 SETUP

### Step 1: Enable Remote Debugging

Edge must be launched with CDP enabled for automation:

```powershell
# Manual Launch
Start-Process "msedge.exe" "--remote-debugging-port=9222"

# OR Use ONI Launcher (Recommended)
.\ONI_Edge_Launcher.ps1 -CDPPort 9222
```

### Step 2: Verify Connection

```powershell
# Test CDP endpoint
Invoke-RestMethod -Uri "http://localhost:9222/json/version"
```

Should return browser version info.

### Step 3: Run Harvester

```powershell
.\ONI_Edge_Harvester.ps1
```

Extracts all profiles, bookmarks, history, extensions.

---

## 🚀 QUICK START

### Launch Edge with ONI Control

```powershell
# Basic launch
.\ONI_Edge_Launcher.ps1

# Development mode
.\ONI_Edge_Launcher.ps1 -Profile "Dev" -Maximized

# Incognito with custom URL
.\ONI_Edge_Launcher.ps1 -Incognito -StartURL "https://example.com"

# Kiosk mode (fullscreen, no UI)
.\ONI_Edge_Launcher.ps1 -Kiosk -StartURL "https://dashboard.com"

# Custom user agent
.\ONI_Edge_Launcher.ps1 -UserAgent "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
```

### Start Real-Time Monitor

```powershell
.\ONI_Edge_Sentinel.ps1 -PollInterval 2
```

**Monitors:**
- ✨ New tabs opened
- 🔄 Page navigations
- ❌ Tabs closed
- 📥 File downloads
- 📊 Session statistics

---

## 💻 JAVASCRIPT API USAGE

### Setup (Node.js or Browser Console)

```javascript
// In Node.js
const ONI = require('./oni_lib_edge.js');

// In Browser Console (paste the entire oni_lib_edge.js file first)
// ONI is now available globally

// Connect to Edge
await ONI.Core.Connect(9222);
console.log('Connected to Edge!');
```

### Tab Management

```javascript
// List all open tabs
const tabs = await ONI.Tab.List();
console.log(`Open tabs: ${tabs.length}`);

tabs.forEach(tab => {
    console.log(`- ${tab.title}`);
});

// Create new tab
const newTab = await ONI.Tab.Create('https://github.com');
console.log(`New tab ID: ${newTab.id}`);

// Navigate current tab
await ONI.Tab.Navigate('https://example.com');

// Reload page
await ONI.Tab.Reload(true); // true = ignore cache

// Close tab by ID
await ONI.Tab.Close(tabId);
```

### Page Interaction

```javascript
// Connect to active tab first
await ONI.Core.Connect();

// Execute JavaScript
const title = await ONI.Page.Eval('document.title');
console.log(`Page title: ${title}`);

// Click element
await ONI.Page.Click('#submit-button');

// Type text
await ONI.Page.Type('input[name="email"]', 'user@example.com');
await ONI.Page.Type('input[name="password"]', 'secretpass');

// Wait for element to appear
await ONI.Page.WaitForSelector('.success-message', 5000);

// Get element text
const message = await ONI.Page.GetText('.notification');

// Scroll to element
await ONI.Page.ScrollTo('.footer');

// Get page URL
const url = await ONI.Page.GetURL();
console.log(`Current URL: ${url}`);
```

### Screenshots & PDF

```javascript
// Take screenshot (returns base64)
const screenshot = await ONI.Capture.Screenshot({
    format: 'png',
    quality: 100
});

// Save screenshot
const fs = require('fs');
fs.writeFileSync('screenshot.png', screenshot, 'base64');

// Full page screenshot
const fullPage = await ONI.Capture.FullScreenshot();

// Generate PDF
const pdf = await ONI.Capture.PrintToPDF({
    landscape: false,
    printBackground: true,
    marginTop: 0.5,
    marginBottom: 0.5
});

fs.writeFileSync('page.pdf', pdf, 'base64');
```

### Cookies & Storage

```javascript
// Get all cookies
const cookies = await ONI.Storage.GetCookies();
console.log(`Total cookies: ${cookies.length}`);

// Set cookie
await ONI.Storage.SetCookie('session_id', 'abc123', {
    domain: 'example.com',
    path: '/',
    secure: true,
    httpOnly: true
});

// Delete cookie
await ONI.Storage.DeleteCookie('old_cookie', 'example.com');

// Clear all cookies
await ONI.Storage.ClearCookies();

// Local Storage
const storage = await ONI.Storage.GetLocalStorage();
console.log('LocalStorage:', storage);

await ONI.Storage.SetLocalStorage('user_pref', 'dark_mode');

await ONI.Storage.ClearLocalStorage();
```

### Network Monitoring

```javascript
// Start monitoring network requests
await ONI.Network.StartMonitoring();

// ... browse around ...

// Get captured requests
const requests = ONI.Network.GetRequests();
console.log(`Captured ${requests.length} requests`);

requests.forEach(req => {
    console.log(`${req.method} ${req.url}`);
});

// Stop monitoring
await ONI.Network.StopMonitoring();

// Block URLs (ad blockers, trackers)
await ONI.Network.BlockURLs([
    '*google-analytics.com*',
    '*facebook.com/tr*',
    '*doubleclick.net*'
]);
```

### Automation Templates

```javascript
// Auto-login
await ONI.Automation.Login(
    'https://example.com/login',
    'myusername',
    'mypassword',
    {
        username: 'input#email',
        password: 'input#password',
        submit: 'button[type="submit"]'
    }
);

// Fill form
await ONI.Automation.FillForm({
    'input[name="firstName"]': 'John',
    'input[name="lastName"]': 'Doe',
    'input[name="email"]': 'john@example.com',
    'select[name="country"]': 'USA'
});

// Scrape table data
const tableData = await ONI.Automation.ScrapeTable('table.data');
console.log(tableData);

// Extract all links
const links = await ONI.Automation.ExtractLinks();
links.forEach(link => {
    console.log(`${link.text} -> ${link.href}`);
});

// Auto-scroll to bottom (infinite scroll pages)
await ONI.Automation.ScrollToBottom(200); // 200ms delay
```

### Browser Control

```javascript
// Get browser version
const version = await ONI.Browser.GetVersion();
console.log(version.Browser);

// Get memory usage
const memory = await ONI.Browser.GetMemoryUsage();
console.log(`Documents: ${memory.documents}`);
console.log(`Nodes: ${memory.nodes}`);

// Set custom user agent
await ONI.Browser.SetUserAgent(
    'Mozilla/5.0 (iPad; CPU OS 13_0 like Mac OS X)',
    'iPad'
);

// Disable JavaScript (for security testing)
await ONI.Browser.SetJavaScriptEnabled(false);

// Clear browser data
await ONI.Browser.ClearData({
    dataTypes: ['cache', 'cookies', 'localStorage']
});
```

---

## 🎯 REAL-WORLD USE CASES

### 1. Automated Testing

```javascript
// Test login flow
await ONI.Tab.Navigate('https://myapp.com/login');
await ONI.Page.Type('#email', 'test@example.com');
await ONI.Page.Type('#password', 'testpass');
await ONI.Page.Click('button[type="submit"]');

await ONI.Page.WaitForSelector('.dashboard', 5000);

const dashboardVisible = await ONI.Page.Eval(
    "!!document.querySelector('.dashboard')"
);

if (dashboardVisible) {
    console.log('✓ Login test PASSED');
} else {
    console.error('✗ Login test FAILED');
}
```

### 2. Web Scraping

```javascript
// Scrape product prices
await ONI.Tab.Navigate('https://ecommerce.com/products');

const products = await ONI.Page.Eval(`
    Array.from(document.querySelectorAll('.product')).map(p => ({
        name: p.querySelector('.title').textContent,
        price: p.querySelector('.price').textContent,
        url: p.querySelector('a').href
    }))
`);

console.log(`Scraped ${products.length} products`);
console.log(products);
```

### 3. Automated Data Entry

```javascript
// Read CSV and fill forms
const csvData = [
    { name: 'John Doe', email: 'john@example.com', phone: '555-0001' },
    { name: 'Jane Smith', email: 'jane@example.com', phone: '555-0002' }
];

for (const record of csvData) {
    await ONI.Tab.Navigate('https://forms.com/submit');
    
    await ONI.Page.WaitForSelector('input[name="name"]');
    await ONI.Page.Type('input[name="name"]', record.name);
    await ONI.Page.Type('input[name="email"]', record.email);
    await ONI.Page.Type('input[name="phone"]', record.phone);
    
    await ONI.Page.Click('button[type="submit"]');
    
    await ONI.Page.WaitForSelector('.success', 3000);
    console.log(`✓ Submitted: ${record.name}`);
}
```

### 4. Monitoring Dashboard

```javascript
// Check website status every 5 minutes
setInterval(async () => {
    const startTime = Date.now();
    
    await ONI.Tab.Navigate('https://mysite.com/status');
    
    const status = await ONI.Page.GetText('.status-indicator');
    const loadTime = Date.now() - startTime;
    
    console.log(`[${new Date().toISOString()}]`);
    console.log(`  Status: ${status}`);
    console.log(`  Load Time: ${loadTime}ms`);
    
    if (status !== 'OK' || loadTime > 3000) {
        // Send alert
        console.error('⚠️ ALERT: Website issue detected!');
    }
}, 5 * 60 * 1000);
```

### 5. Screenshot Bot

```javascript
// Take screenshots of multiple pages
const urls = [
    'https://example.com',
    'https://example.com/products',
    'https://example.com/about'
];

for (const url of urls) {
    await ONI.Tab.Navigate(url);
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for load
    
    const screenshot = await ONI.Capture.Screenshot();
    const filename = url.replace(/[^a-z0-9]/gi, '_') + '.png';
    
    require('fs').writeFileSync(filename, screenshot, 'base64');
    console.log(`✓ Saved: ${filename}`);
}
```

### 6. Cookie Manager

```javascript
// Export cookies for session transfer
const cookies = await ONI.Storage.GetCookies();

// Save to file
require('fs').writeFileSync(
    'session_cookies.json',
    JSON.stringify(cookies, null, 2)
);

// Later: Import cookies
const savedCookies = JSON.parse(
    require('fs').readFileSync('session_cookies.json')
);

for (const cookie of savedCookies) {
    await ONI.Storage.SetCookie(cookie.name, cookie.value, {
        domain: cookie.domain,
        path: cookie.path
    });
}
```

---

## 🔧 ADVANCED FEATURES

### Profile Management

```powershell
# Launch specific profile
.\ONI_Edge_Launcher.ps1 -Profile "WorkProfile"

# Create profile isolation
.\ONI_Edge_Launcher.ps1 -Profile "Testing" -Incognito
```

### Custom Flags

```powershell
# Disable images for faster loading
.\ONI_Edge_Launcher.ps1 -CustomFlags @(
    "--blink-settings=imagesEnabled=false"
)

# Disable web security (TESTING ONLY)
.\ONI_Edge_Launcher.ps1 -CustomFlags @(
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process"
)
```

### Multi-Tab Orchestration

```javascript
// Open multiple tabs and orchestrate
const tab1 = await ONI.Tab.Create('https://site1.com');
const tab2 = await ONI.Tab.Create('https://site2.com');
const tab3 = await ONI.Tab.Create('https://site3.com');

// Connect to specific tab
await ONI.Core.ConnectToTab(tab1.id);
const data1 = await ONI.Page.Eval('document.title');

await ONI.Core.ConnectToTab(tab2.id);
const data2 = await ONI.Page.Eval('document.title');

console.log('Tab 1:', data1);
console.log('Tab 2:', data2);
```

---

## 📊 MONITORING & ANALYTICS

### Real-Time Statistics

The Sentinel provides:
- Tabs opened/closed count
- Navigation tracking
- Download monitoring
- Session duration
- Activity timeline

Access via `sentinel_log.txt` or dashboard integration.

### Browser Health

```javascript
const memory = await ONI.Browser.GetMemoryUsage();
console.log('Memory Health:');
console.log(`  Documents: ${memory.documents}`);
console.log(`  DOM Nodes: ${memory.nodes}`);
console.log(`  JS Event Listeners: ${memory.jsEventListeners}`);
```

---

## 🛡️ SECURITY NOTES

### ⚠️ Remote Debugging Risks

Running Edge with `--remote-debugging-port` exposes full browser control to localhost. **Never** expose CDP port to external networks.

### Recommendations:

1. **Firewall:** Block CDP port (9222) from external access
2. **Dedicated Profile:** Use separate profile for automation
3. **No Sensitive Data:** Don't use for banking, personal accounts
4. **Credential Management:** Never hardcode passwords in scripts
5. **Regular Audits:** Review sentinel logs for suspicious activity

---

## 🚨 TROUBLESHOOTING

### "Connection refused" Error

```
Solution: Edge not launched with --remote-debugging-port
Fix: .\ONI_Edge_Launcher.ps1 -CDPPort 9222
```

### "Target closed" Error

```
Solution: Tab was closed during operation
Fix: Add try-catch and reconnect logic
```

### Sentinel Not Detecting Changes

```
Solution: CDP not enabled
Fix: Restart Edge with launcher script
```

### "Could not find element" Error

```
Solution: Page not fully loaded or selector wrong
Fix: Use ONI.Page.WaitForSelector() before interaction
```

---

## 📚 ADDITIONAL RESOURCES

- **Chrome DevTools Protocol Docs:** https://chromedevtools.github.io/devtools-protocol/
- **Edge WebDriver:** https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
- **ONI Support:** (Your internal channel)

---

## 🎉 EXAMPLE WORKFLOW

```powershell
# 1. Launch Edge with ONI
.\ONI_Edge_Launcher.ps1 -Profile "Automation" -Maximized

# 2. Start monitoring
Start-Process PowerShell -ArgumentList "-File .\ONI_Edge_Sentinel.ps1"

# 3. Run automation (Node.js)
node my_automation.js

# 4. Review logs
Get-Content C:\ONI\Edge\sentinel_log.txt -Tail 50
```

```javascript
// my_automation.js
const ONI = require('./oni_lib_edge.js');

(async () => {
    await ONI.Core.Connect(9222);
    
    // Your automation here
    await ONI.Tab.Navigate('https://example.com');
    const title = await ONI.Page.GetTitle();
    console.log(`Page loaded: ${title}`);
    
    // Take screenshot
    const screenshot = await ONI.Capture.Screenshot();
    require('fs').writeFileSync('result.png', screenshot, 'base64');
    
    ONI.Core.Disconnect();
})();
```

---

**System Status:** ✅ OPERATIONAL  
**Version:** 1.0  
**Last Updated:** January 2026