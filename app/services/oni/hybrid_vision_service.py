import json
import base64
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class Element:
    """Representa um elemento interativo da página"""
    id: str
    role: str
    label: str
    tag_name: str
    is_clickable: bool
    is_editable: bool
    is_focusable: bool
    coordinates: Dict[str, int]
    selector: str
    attributes: Dict[str, str]
    text_content: str
    parent_id: Optional[str] = None
    children: List[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class AccessibilityNode:
    """Nó da Accessibility Tree"""
    role: str
    name: str
    focusable: bool
    editable: bool
    required: bool
    element_id: str
    children: List['AccessibilityNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def to_dict(self):
        return {
            'role': self.role,
            'name': self.name,
            'focusable': self.focusable,
            'editable': self.editable,
            'required': self.required,
            'element_id': self.element_id,
            'children': [c.to_dict() for c in self.children]
        }

@dataclass
class HybridVisionResult:
    """Resultado completo da análise híbrida"""
    screenshot_base64: str
    screenshot_path: str
    url: str
    title: str
    viewport_size: Dict[str, int]
    elements: List[Element]
    ax_tree: AccessibilityNode
    scene_description: str
    clickable_elements: List[Dict]
    editable_elements: List[Dict]
    navigation_elements: List[Dict]
    
    def to_dict(self):
        return {
            'screenshot_base64': self.screenshot_base64,
            'screenshot_path': self.screenshot_path,
            'url': self.url,
            'title': self.title,
            'viewport_size': self.viewport_size,
            'elements': [asdict(e) for e in self.elements],
            'ax_tree': self.ax_tree.to_dict(),
            'scene_description': self.scene_description,
            'clickable_elements': self.clickable_elements,
            'editable_elements': self.editable_elements,
            'navigation_elements': self.navigation_elements
        }

class HybridVisionService:
    """Serviço de Visão Híbrida (Browser Subagent Engine)"""
    
    AX_TREE_SCRIPT = """
    function buildAXTree(element) {
        const role = element.getAttribute('role') || element.tagName.toLowerCase();
        const name = element.getAttribute('aria-label') || 
                     element.getAttribute('alt') || 
                     element.getAttribute('title') ||
                     element.textContent?.trim().substring(0, 50) || '';
        
        const focusable = element.tabIndex >= 0 || 
                         ['a', 'button', 'input', 'select', 'textarea'].includes(element.tagName.toLowerCase());
        
        const editable = element.isContentEditable || 
                        ['input', 'textarea'].includes(element.tagName.toLowerCase());
        
        const required = element.hasAttribute('required') || 
                        element.getAttribute('aria-required') === 'true';
        
        const node = {
            role: role,
            name: name,
            focusable: focusable,
            editable: editable,
            required: required,
            element_id: element.getAttribute('data-vision-id') || '',
            children: []
        };
        
        const children = Array.from(element.children).filter(child => {
            const tag = child.tagName.toLowerCase();
            return ['a', 'button', 'input', 'select', 'textarea', 'form', 'nav'].includes(tag) ||
                   child.getAttribute('role') || child.tabIndex >= 0;
        });
        
        node.children = children.map(child => buildAXTree(child));
        return node;
    }
    return buildAXTree(document.body);
    """
    
    EXTRACT_ELEMENTS_SCRIPT = """
    const elements = [];
    let idCounter = 0;
    
    function getSelector(element) {
        if (element.id) return `#${element.id}`;
        if (element.className) {
            const classes = element.className.split(' ').filter(c => c).join('.');
            if (classes) return `${element.tagName.toLowerCase()}.${classes}`;
        }
        return element.tagName.toLowerCase();
    }
    
    function extractElement(el) {
        const rect = el.getBoundingClientRect();
        const visionId = `elem_${idCounter++}`;
        el.setAttribute('data-vision-id', visionId);
        
        const isClickable = el.tagName.toLowerCase() === 'a' || 
                           el.tagName.toLowerCase() === 'button' ||
                           el.onclick !== null ||
                           el.getAttribute('role') === 'button' ||
                           getComputedStyle(el).cursor === 'pointer';
        
        const isEditable = el.isContentEditable || 
                          ['input', 'textarea', 'select'].includes(el.tagName.toLowerCase());
        
        const isFocusable = el.tabIndex >= 0 || 
                           ['a', 'button', 'input', 'select', 'textarea'].includes(el.tagName.toLowerCase());
        
        return {
            id: visionId,
            role: el.getAttribute('role') || el.tagName.toLowerCase(),
            label: el.getAttribute('aria-label') || el.getAttribute('alt') || el.textContent?.trim().substring(0, 100) || '',
            tag_name: el.tagName.toLowerCase(),
            is_clickable: isClickable,
            is_editable: isEditable,
            is_focusable: isFocusable,
            coordinates: {
                x: Math.round(rect.left + window.scrollX),
                y: Math.round(rect.top + window.scrollY),
                width: Math.round(rect.width),
                height: Math.round(rect.height),
                center_x: Math.round(rect.left + rect.width / 2 + window.scrollX),
                center_y: Math.round(rect.top + rect.height / 2 + window.scrollY)
            },
            selector: getSelector(el),
            attributes: {
                id: el.id || '',
                class: el.className || '',
                href: el.href || '',
                type: el.type || '',
                name: el.name || '',
                placeholder: el.placeholder || '',
                value: el.value || ''
            },
            text_content: el.textContent?.trim().substring(0, 200) || ''
        };
    }
    
    const interactiveSelectors = 'a, button, input, select, textarea, [role="button"], [onclick], [tabindex]';
    document.querySelectorAll(interactiveSelectors).forEach(el => {
        if (el.offsetParent !== null) { 
            elements.push(extractElement(el));
        }
    });
    return elements;
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        if self.driver:
            return
            
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        # Use WebDriver Manager to ensure driver exists
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(30)

    def analyze(self, url: str) -> HybridVisionResult:
        try:
            self._init_driver()
            
            logger.info("loading_page", url=url)
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Screenshot
            screenshot_bytes = self.driver.get_screenshot_as_png()
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            # DOM Extraction
            elements_data = self.driver.execute_script(self.EXTRACT_ELEMENTS_SCRIPT)
            elements = [Element(**data) for data in elements_data]
            
            # Accessibility Tree
            ax_tree_data = self.driver.execute_script(self.AX_TREE_SCRIPT)
            
            def parse_node(data: Dict) -> AccessibilityNode:
                node = AccessibilityNode(
                    role=data['role'],
                    name=data['name'],
                    focusable=data['focusable'],
                    editable=data['editable'],
                    required=data['required'],
                    element_id=data['element_id']
                )
                for child in data['children']:
                    node.children.append(parse_node(child))
                return node
                
            ax_tree = parse_node(ax_tree_data)
            
            # Categorize
            clickable = [asdict(e) for e in elements if e.is_clickable]
            editable = [asdict(e) for e in elements if e.is_editable]
            navigation = [asdict(e) for e in elements if e.role in ['a', 'nav', 'link'] or e.tag_name == 'a']
            
            # Scene Description
            description = f"Page '{self.driver.title}' loaded.\n"
            description += f"Found {len(elements)} interactive elements ({len(clickable)} clickable, {len(editable)} editable)."
            
            viewport = {
                'width': self.driver.execute_script("return window.innerWidth"),
                'height': self.driver.execute_script("return window.innerHeight")
            }
            
            return HybridVisionResult(
                screenshot_base64=screenshot_b64,
                screenshot_path="",
                url=url,
                title=self.driver.title,
                viewport_size=viewport,
                elements=elements,
                ax_tree=ax_tree,
                scene_description=description,
                clickable_elements=clickable,
                editable_elements=editable,
                navigation_elements=navigation
            )
            
        except Exception as e:
            logger.error("hybrid_analysis_failed", error=str(e))
            raise

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
