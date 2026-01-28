/*
 * ONI CORE LIBRARY - MICROSOFT EDGE AUTOMATION
 * Version: 1.0 (Total Browser Control)
 * 
 * Standardized High-Level Functions for Browser Automation & Management.
 * Usage: Chrome DevTools Protocol (CDP) via WebSocket connection.
 */

const ONI = ONI || {};

// ============================================================================
// MODULE: CORE UTILITIES
// ============================================================================
ONI.Core = {
    // Connection Configuration
    config: {
        host: 'localhost',
        port: 9222,
        wsEndpoint: null,
        targetId: null
    },

    // WebSocket Connection
    ws: null,
    messageId: 0,
    callbacks: new Map(),

    // Connect to Edge via CDP
    Connect: async function(port = 9222) {
        this.config.port = port;
        
        // Get available targets
        const response = await fetch(`http://${this.config.host}:${port}/json/version`);
        const version = await response.json();
        this.config.wsEndpoint = version.webSocketDebuggerUrl;
        
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.config.wsEndpoint);
            
            this.ws.onopen = () => {
                console.log('ONI.Edge: Connected to Edge CDP');
                resolve(true);
            };
            
            this.ws.onerror = (error) => {
                console.error('ONI.Edge: Connection failed', error);
                reject(error);
            };
            
            this.ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                
                if (message.id && this.callbacks.has(message.id)) {
                    const callback = this.callbacks.get(message.id);
                    callback(message);
                    this.callbacks.delete(message.id);
                }
            };
        });
    },

    // Send CDP Command
    Send: function(method, params = {}) {
        return new Promise((resolve, reject) => {
            const id = ++this.messageId;
            const message = { id, method, params };
            
            this.callbacks.set(id, (response) => {
                if (response.error) {
                    reject(new Error(response.error.message));
                } else {
                    resolve(response.result);
                }
            });
            
            this.ws.send(JSON.stringify(message));
            
            // Timeout after 30 seconds
            setTimeout(() => {
                if (this.callbacks.has(id)) {
                    this.callbacks.delete(id);
                    reject(new Error('Command timeout'));
                }
            }, 30000);
        });
    },

    // Get All Open Tabs
    GetTabs: async function() {
        const response = await fetch(`http://${this.config.host}:${this.config.port}/json`);
        return await response.json();
    },

    // Connect to Specific Tab
    ConnectToTab: async function(tabId) {
        const tabs = await this.GetTabs();
        const tab = tabs.find(t => t.id === tabId);
        
        if (!tab) throw new Error('Tab not found');
        
        this.config.wsEndpoint = tab.webSocketDebuggerUrl;
        await this.Connect();
        return tab;
    },

    // Close Connection
    Disconnect: function() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
};

// ============================================================================
// MODULE: BROWSER CONTROL
// ============================================================================
ONI.Browser = {
    // Get Browser Version
    GetVersion: async function() {
        const response = await fetch(`http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/version`);
        return await response.json();
    },

    // Close Browser
    Close: async function() {
        await fetch(`http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/close`, {
            method: 'GET'
        });
    },

    // Get Browser Memory Usage
    GetMemoryUsage: async function() {
        return await ONI.Core.Send('Memory.getDOMCounters');
    },

    // Clear Browser Data
    ClearData: async function(options = {}) {
        const dataTypes = options.dataTypes || [
            'cache',
            'cookies',
            'localStorage',
            'indexedDB'
        ];
        
        return await ONI.Core.Send('Storage.clearDataForOrigin', {
            origin: '*',
            storageTypes: dataTypes.join(',')
        });
    },

    // Set User Agent
    SetUserAgent: async function(userAgent, platform = 'Windows') {
        return await ONI.Core.Send('Network.setUserAgentOverride', {
            userAgent: userAgent,
            platform: platform
        });
    },

    // Enable/Disable JavaScript
    SetJavaScriptEnabled: async function(enabled) {
        return await ONI.Core.Send('Emulation.setScriptExecutionDisabled', {
            value: !enabled
        });
    }
};

// ============================================================================
// MODULE: TAB MANAGEMENT
// ============================================================================
ONI.Tab = {
    // Create New Tab
    Create: async function(url = 'about:blank') {
        const response = await fetch(
            `http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/new?${url}`
        );
        return await response.json();
    },

    // Close Tab
    Close: async function(tabId) {
        await fetch(
            `http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/close/${tabId}`
        );
    },

    // Activate Tab
    Activate: async function(tabId) {
        await fetch(
            `http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/activate/${tabId}`
        );
    },

    // Get Tab Info
    Get: async function(tabId) {
        const tabs = await ONI.Core.GetTabs();
        return tabs.find(t => t.id === tabId);
    },

    // List All Tabs
    List: async function() {
        return await ONI.Core.GetTabs();
    },

    // Reload Tab
    Reload: async function(ignoreCache = false) {
        return await ONI.Core.Send('Page.reload', {
            ignoreCache: ignoreCache
        });
    },

    // Navigate to URL
    Navigate: async function(url) {
        return await ONI.Core.Send('Page.navigate', { url });
    },

    // Go Back
    Back: async function() {
        const history = await ONI.Core.Send('Page.getNavigationHistory');
        if (history.currentIndex > 0) {
            return await ONI.Core.Send('Page.navigateToHistoryEntry', {
                entryId: history.entries[history.currentIndex - 1].id
            });
        }
    },

    // Go Forward
    Forward: async function() {
        const history = await ONI.Core.Send('Page.getNavigationHistory');
        if (history.currentIndex < history.entries.length - 1) {
            return await ONI.Core.Send('Page.navigateToHistoryEntry', {
                entryId: history.entries[history.currentIndex + 1].id
            });
        }
    }
};

// ============================================================================
// MODULE: PAGE INTERACTION
// ============================================================================
ONI.Page = {
    // Evaluate JavaScript
    Eval: async function(script) {
        const result = await ONI.Core.Send('Runtime.evaluate', {
            expression: script,
            returnByValue: true
        });
        return result.result.value;
    },

    // Click Element
    Click: async function(selector) {
        const script = `
            const el = document.querySelector('${selector}');
            if (el) {
                el.click();
                true;
            } else {
                false;
            }
        `;
        return await this.Eval(script);
    },

    // Type Text
    Type: async function(selector, text) {
        const script = `
            const el = document.querySelector('${selector}');
            if (el) {
                el.value = '${text}';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                true;
            } else {
                false;
            }
        `;
        return await this.Eval(script);
    },

    // Get Element Text
    GetText: async function(selector) {
        const script = `
            const el = document.querySelector('${selector}');
            el ? el.textContent : null;
        `;
        return await this.Eval(script);
    },

    // Get Element Attribute
    GetAttribute: async function(selector, attribute) {
        const script = `
            const el = document.querySelector('${selector}');
            el ? el.getAttribute('${attribute}') : null;
        `;
        return await this.Eval(script);
    },

    // Wait for Selector
    WaitForSelector: async function(selector, timeout = 30000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const exists = await this.Eval(`!!document.querySelector('${selector}')`);
            if (exists) return true;
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        throw new Error(`Selector '${selector}' not found within ${timeout}ms`);
    },

    // Scroll To Element
    ScrollTo: async function(selector) {
        const script = `
            const el = document.querySelector('${selector}');
            if (el) {
                el.scrollIntoView({ behavior: 'smooth' });
                true;
            } else {
                false;
            }
        `;
        return await this.Eval(script);
    },

    // Get Page Title
    GetTitle: async function() {
        return await this.Eval('document.title');
    },

    // Get Page URL
    GetURL: async function() {
        return await this.Eval('window.location.href');
    },

    // Get Page HTML
    GetHTML: async function() {
        return await this.Eval('document.documentElement.outerHTML');
    },

    // Inject CSS
    InjectCSS: async function(css) {
        const script = `
            const style = document.createElement('style');
            style.textContent = \`${css}\`;
            document.head.appendChild(style);
            true;
        `;
        return await this.Eval(script);
    },

    // Inject JavaScript
    InjectJS: async function(script) {
        return await this.Eval(script);
    }
};

// ============================================================================
// MODULE: SCREENSHOT & PDF
// ============================================================================
ONI.Capture = {
    // Take Screenshot
    Screenshot: async function(options = {}) {
        const params = {
            format: options.format || 'png',
            quality: options.quality || 100,
            fromSurface: true
        };
        
        if (options.clip) {
            params.clip = options.clip; // {x, y, width, height, scale}
        }
        
        const result = await ONI.Core.Send('Page.captureScreenshot', params);
        return result.data; // Base64 encoded image
    },

    // Full Page Screenshot
    FullScreenshot: async function() {
        // Get page dimensions
        const dimensions = await ONI.Page.Eval(`({
            width: document.documentElement.scrollWidth,
            height: document.documentElement.scrollHeight
        })`);
        
        return await this.Screenshot({
            clip: {
                x: 0,
                y: 0,
                width: dimensions.width,
                height: dimensions.height,
                scale: 1
            }
        });
    },

    // Generate PDF
    PrintToPDF: async function(options = {}) {
        const params = {
            landscape: options.landscape || false,
            displayHeaderFooter: options.headerFooter || false,
            printBackground: options.printBackground !== false,
            scale: options.scale || 1,
            paperWidth: options.paperWidth || 8.5,
            paperHeight: options.paperHeight || 11,
            marginTop: options.marginTop || 0,
            marginBottom: options.marginBottom || 0,
            marginLeft: options.marginLeft || 0,
            marginRight: options.marginRight || 0
        };
        
        const result = await ONI.Core.Send('Page.printToPDF', params);
        return result.data; // Base64 encoded PDF
    }
};

// ============================================================================
// MODULE: COOKIES & STORAGE
// ============================================================================
ONI.Storage = {
    // Get All Cookies
    GetCookies: async function(urls = []) {
        const params = urls.length > 0 ? { urls } : {};
        const result = await ONI.Core.Send('Network.getCookies', params);
        return result.cookies;
    },

    // Set Cookie
    SetCookie: async function(name, value, options = {}) {
        const cookie = {
            name: name,
            value: value,
            domain: options.domain || window.location.hostname,
            path: options.path || '/',
            secure: options.secure || false,
            httpOnly: options.httpOnly || false,
            sameSite: options.sameSite || 'Lax'
        };
        
        if (options.expires) cookie.expires = options.expires;
        
        return await ONI.Core.Send('Network.setCookie', cookie);
    },

    // Delete Cookie
    DeleteCookie: async function(name, domain) {
        return await ONI.Core.Send('Network.deleteCookies', {
            name: name,
            domain: domain || window.location.hostname
        });
    },

    // Clear All Cookies
    ClearCookies: async function() {
        return await ONI.Core.Send('Network.clearBrowserCookies');
    },

    // Get Local Storage
    GetLocalStorage: async function() {
        return await ONI.Page.Eval(`
            Object.entries(localStorage).reduce((acc, [k, v]) => {
                acc[k] = v;
                return acc;
            }, {})
        `);
    },

    // Set Local Storage
    SetLocalStorage: async function(key, value) {
        return await ONI.Page.Eval(`
            localStorage.setItem('${key}', '${value}');
            true;
        `);
    },

    // Clear Local Storage
    ClearLocalStorage: async function() {
        return await ONI.Page.Eval('localStorage.clear(); true;');
    }
};

// ============================================================================
// MODULE: NETWORK MONITORING
// ============================================================================
ONI.Network = {
    requests: [],
    monitoring: false,

    // Start Monitoring
    StartMonitoring: async function() {
        await ONI.Core.Send('Network.enable');
        this.monitoring = true;
        
        // Listen for requests
        ONI.Core.ws.addEventListener('message', (event) => {
            const message = JSON.parse(event.data);
            
            if (message.method === 'Network.requestWillBeSent') {
                this.requests.push({
                    requestId: message.params.requestId,
                    url: message.params.request.url,
                    method: message.params.request.method,
                    headers: message.params.request.headers,
                    timestamp: message.params.timestamp
                });
            }
        });
    },

    // Stop Monitoring
    StopMonitoring: async function() {
        await ONI.Core.Send('Network.disable');
        this.monitoring = false;
    },

    // Get Captured Requests
    GetRequests: function() {
        return this.requests;
    },

    // Clear Captured Requests
    ClearRequests: function() {
        this.requests = [];
    },

    // Block URLs
    BlockURLs: async function(patterns) {
        return await ONI.Core.Send('Network.setBlockedURLs', {
            urls: patterns
        });
    },

    // Set Download Behavior
    SetDownloadBehavior: async function(behavior = 'allow', downloadPath = null) {
        const params = { behavior };
        if (downloadPath) params.downloadPath = downloadPath;
        
        return await ONI.Core.Send('Page.setDownloadBehavior', params);
    }
};

// ============================================================================
// MODULE: AUTOMATION TEMPLATES
// ============================================================================
ONI.Automation = {
    // Auto-Fill Form
    FillForm: async function(formData) {
        for (const [selector, value] of Object.entries(formData)) {
            await ONI.Page.Type(selector, value);
        }
    },

    // Login Helper
    Login: async function(url, username, password, selectors = {}) {
        await ONI.Tab.Navigate(url);
        await ONI.Page.WaitForSelector(selectors.username || 'input[type="text"]');
        
        await ONI.Page.Type(selectors.username || 'input[type="text"]', username);
        await ONI.Page.Type(selectors.password || 'input[type="password"]', password);
        await ONI.Page.Click(selectors.submit || 'button[type="submit"]');
    },

    // Scrape Table
    ScrapeTable: async function(tableSelector) {
        const script = `
            const table = document.querySelector('${tableSelector}');
            if (!table) return null;
            
            const rows = Array.from(table.querySelectorAll('tr'));
            return rows.map(row => {
                return Array.from(row.querySelectorAll('td, th')).map(cell => cell.textContent.trim());
            });
        `;
        return await ONI.Page.Eval(script);
    },

    // Extract Links
    ExtractLinks: async function() {
        return await ONI.Page.Eval(`
            Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.textContent.trim(),
                href: a.href
            }))
        `);
    },

    // Auto-Scroll to Bottom
    ScrollToBottom: async function(delay = 100) {
        const script = `
            (async () => {
                const distance = 100;
                const delay = ${delay};
                
                while (document.documentElement.scrollTop + window.innerHeight < document.documentElement.scrollHeight) {
                    window.scrollBy(0, distance);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            })()
        `;
        return await ONI.Page.Eval(script);
    }
};

// ============================================================================
// MODULE: PROFILE MANAGEMENT
// ============================================================================
ONI.Profile = {
    // Get Profiles (via filesystem - requires Node.js)
    // Edge profiles are stored in: %LOCALAPPDATA%\Microsoft\Edge\User Data\
    
    profilePath: null,

    SetProfilePath: function(path) {
        this.profilePath = path;
    },

    // Note: Profile switching requires restarting Edge with --profile-directory flag
    // This is typically done via PowerShell or command line
};

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ONI;
}