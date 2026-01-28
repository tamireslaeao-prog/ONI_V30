/*
 * ONI CORE LIBRARY - GOOGLE CHROME AUTOMATION
 * Version: 1.0 (CDP-Based Control)
 * 
 * Ported from ONI.Edge.js - Full browser control via Chrome DevTools Protocol
 * Usage: Connect to Chrome launched with --remote-debugging-port=9222
 */

const ONI = ONI || {};

// ============================================================================
// MODULE: CORE UTILITIES
// ============================================================================
ONI.Core = {
    config: {
        host: 'localhost',
        port: 9222,
        wsEndpoint: null,
        targetId: null
    },

    ws: null,
    messageId: 0,
    callbacks: new Map(),

    // Connect to Chrome via CDP
    Connect: async function (port = 9222) {
        this.config.port = port;

        const response = await fetch(`http://${this.config.host}:${port}/json/version`);
        const version = await response.json();
        this.config.wsEndpoint = version.webSocketDebuggerUrl;

        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.config.wsEndpoint);

            this.ws.onopen = () => {
                console.log('ONI.Chrome: Connected to Chrome CDP');
                resolve(true);
            };

            this.ws.onerror = (error) => {
                console.error('ONI.Chrome: Connection failed', error);
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

    Send: function (method, params = {}) {
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

            setTimeout(() => {
                if (this.callbacks.has(id)) {
                    this.callbacks.delete(id);
                    reject(new Error('Command timeout'));
                }
            }, 30000);
        });
    },

    GetTabs: async function () {
        const response = await fetch(`http://${this.config.host}:${this.config.port}/json`);
        return await response.json();
    },

    ConnectToTab: async function (tabId) {
        const tabs = await this.GetTabs();
        const tab = tabs.find(t => t.id === tabId);
        if (!tab) throw new Error('Tab not found');
        this.config.wsEndpoint = tab.webSocketDebuggerUrl;
        await this.Connect();
        return tab;
    },

    Disconnect: function () {
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
    GetVersion: async function () {
        const response = await fetch(`http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/version`);
        return await response.json();
    },

    Close: async function () {
        await fetch(`http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/close`, { method: 'GET' });
    },

    GetMemoryUsage: async function () {
        return await ONI.Core.Send('Memory.getDOMCounters');
    },

    ClearData: async function (options = {}) {
        const dataTypes = options.dataTypes || ['cache', 'cookies', 'localStorage', 'indexedDB'];
        return await ONI.Core.Send('Storage.clearDataForOrigin', {
            origin: '*',
            storageTypes: dataTypes.join(',')
        });
    },

    SetUserAgent: async function (userAgent, platform = 'Windows') {
        return await ONI.Core.Send('Network.setUserAgentOverride', {
            userAgent: userAgent,
            platform: platform
        });
    },

    SetJavaScriptEnabled: async function (enabled) {
        return await ONI.Core.Send('Emulation.setScriptExecutionDisabled', { value: !enabled });
    }
};

// ============================================================================
// MODULE: TAB MANAGEMENT
// ============================================================================
ONI.Tab = {
    Create: async function (url = 'about:blank') {
        const response = await fetch(`http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/new?${url}`);
        return await response.json();
    },

    Close: async function (tabId) {
        await fetch(`http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/close/${tabId}`);
    },

    Activate: async function (tabId) {
        await fetch(`http://${ONI.Core.config.host}:${ONI.Core.config.port}/json/activate/${tabId}`);
    },

    List: async function () {
        return await ONI.Core.GetTabs();
    },

    Reload: async function (ignoreCache = false) {
        return await ONI.Core.Send('Page.reload', { ignoreCache });
    },

    Navigate: async function (url) {
        return await ONI.Core.Send('Page.navigate', { url });
    },

    Back: async function () {
        const history = await ONI.Core.Send('Page.getNavigationHistory');
        if (history.currentIndex > 0) {
            return await ONI.Core.Send('Page.navigateToHistoryEntry', {
                entryId: history.entries[history.currentIndex - 1].id
            });
        }
    },

    Forward: async function () {
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
    Eval: async function (script) {
        const result = await ONI.Core.Send('Runtime.evaluate', {
            expression: script,
            returnByValue: true
        });
        return result.result.value;
    },

    Click: async function (selector) {
        return await this.Eval(`
            const el = document.querySelector('${selector}');
            if (el) { el.click(); true; } else { false; }
        `);
    },

    Type: async function (selector, text) {
        return await this.Eval(`
            const el = document.querySelector('${selector}');
            if (el) {
                el.value = '${text}';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                true;
            } else { false; }
        `);
    },

    GetText: async function (selector) {
        return await this.Eval(`
            const el = document.querySelector('${selector}');
            el ? el.textContent : null;
        `);
    },

    WaitForSelector: async function (selector, timeout = 30000) {
        const startTime = Date.now();
        while (Date.now() - startTime < timeout) {
            const exists = await this.Eval(`!!document.querySelector('${selector}')`);
            if (exists) return true;
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        throw new Error(`Selector '${selector}' not found within ${timeout}ms`);
    },

    ScrollTo: async function (selector) {
        return await this.Eval(`
            const el = document.querySelector('${selector}');
            if (el) { el.scrollIntoView({ behavior: 'smooth' }); true; } else { false; }
        `);
    },

    GetTitle: async function () {
        return await this.Eval('document.title');
    },

    GetURL: async function () {
        return await this.Eval('window.location.href');
    },

    GetHTML: async function () {
        return await this.Eval('document.documentElement.outerHTML');
    }
};

// ============================================================================
// MODULE: SCREENSHOT & PDF
// ============================================================================
ONI.Capture = {
    Screenshot: async function (options = {}) {
        const params = {
            format: options.format || 'png',
            quality: options.quality || 100,
            fromSurface: true
        };
        if (options.clip) params.clip = options.clip;
        const result = await ONI.Core.Send('Page.captureScreenshot', params);
        return result.data;
    },

    FullScreenshot: async function () {
        const dimensions = await ONI.Page.Eval(`({
            width: document.documentElement.scrollWidth,
            height: document.documentElement.scrollHeight
        })`);
        return await this.Screenshot({
            clip: { x: 0, y: 0, width: dimensions.width, height: dimensions.height, scale: 1 }
        });
    },

    PrintToPDF: async function (options = {}) {
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
        return result.data;
    }
};

// ============================================================================
// MODULE: COOKIES & STORAGE
// ============================================================================
ONI.Storage = {
    GetCookies: async function (urls = []) {
        const params = urls.length > 0 ? { urls } : {};
        const result = await ONI.Core.Send('Network.getCookies', params);
        return result.cookies;
    },

    SetCookie: async function (name, value, options = {}) {
        return await ONI.Core.Send('Network.setCookie', {
            name, value,
            domain: options.domain || 'localhost',
            path: options.path || '/',
            secure: options.secure || false,
            httpOnly: options.httpOnly || false,
            sameSite: options.sameSite || 'Lax',
            expires: options.expires
        });
    },

    DeleteCookie: async function (name, domain) {
        return await ONI.Core.Send('Network.deleteCookies', { name, domain: domain || 'localhost' });
    },

    ClearCookies: async function () {
        return await ONI.Core.Send('Network.clearBrowserCookies');
    },

    GetLocalStorage: async function () {
        return await ONI.Page.Eval(`
            Object.entries(localStorage).reduce((acc, [k, v]) => { acc[k] = v; return acc; }, {})
        `);
    },

    SetLocalStorage: async function (key, value) {
        return await ONI.Page.Eval(`localStorage.setItem('${key}', '${value}'); true;`);
    },

    ClearLocalStorage: async function () {
        return await ONI.Page.Eval('localStorage.clear(); true;');
    }
};

// ============================================================================
// MODULE: NETWORK MONITORING
// ============================================================================
ONI.Network = {
    requests: [],
    monitoring: false,

    StartMonitoring: async function () {
        await ONI.Core.Send('Network.enable');
        this.monitoring = true;

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

    StopMonitoring: async function () {
        await ONI.Core.Send('Network.disable');
        this.monitoring = false;
    },

    GetRequests: function () {
        return this.requests;
    },

    ClearRequests: function () {
        this.requests = [];
    },

    BlockURLs: async function (patterns) {
        return await ONI.Core.Send('Network.setBlockedURLs', { urls: patterns });
    }
};

// ============================================================================
// MODULE: AUTOMATION TEMPLATES
// ============================================================================
ONI.Automation = {
    FillForm: async function (formData) {
        for (const [selector, value] of Object.entries(formData)) {
            await ONI.Page.Type(selector, value);
        }
    },

    Login: async function (url, username, password, selectors = {}) {
        await ONI.Tab.Navigate(url);
        await ONI.Page.WaitForSelector(selectors.username || 'input[type="text"]');
        await ONI.Page.Type(selectors.username || 'input[type="text"]', username);
        await ONI.Page.Type(selectors.password || 'input[type="password"]', password);
        await ONI.Page.Click(selectors.submit || 'button[type="submit"]');
    },

    ScrapeTable: async function (tableSelector) {
        return await ONI.Page.Eval(`
            const table = document.querySelector('${tableSelector}');
            if (!table) return null;
            const rows = Array.from(table.querySelectorAll('tr'));
            return rows.map(row => Array.from(row.querySelectorAll('td, th')).map(cell => cell.textContent.trim()));
        `);
    },

    ExtractLinks: async function () {
        return await ONI.Page.Eval(`
            Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.textContent.trim(),
                href: a.href
            }))
        `);
    },

    ScrollToBottom: async function (delay = 100) {
        return await ONI.Page.Eval(`
            (async () => {
                const distance = 100;
                while (document.documentElement.scrollTop + window.innerHeight < document.documentElement.scrollHeight) {
                    window.scrollBy(0, distance);
                    await new Promise(resolve => setTimeout(resolve, ${delay}));
                }
            })()
        `);
    }
};

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ONI;
}
