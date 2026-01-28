
import os
import sys
import time
import requests
import json
import base64

# Simple .env parser to avoid extra dependencies
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

ENV = load_env()
STABILITY_API_KEY = ENV.get("STABILITY_API_KEY")
NANO_API_KEY = ENV.get("NANO_API_KEY") # Gemini

def generate_image_nanobanana(prompt, output_dir="temp"):
    """
    Generates an image using Stability AI (SDXL) via API.
    Fallback: Gemini (Nano) if implemented, otherwise Error.
    """
    print(f"\n[NANOBANANA] AI GENERATION")
    print(f"-------------------------------")
    print(f"Prompt: {prompt}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize prompt for filename
    safe_prompt = "".join([c for c in prompt if c.isalnum() or c in (' ', '_')]).rstrip()
    safe_prompt = safe_prompt.replace(" ", "_")[:30]
    output_filename = f"nano_{safe_prompt}_{int(time.time())}.png"
    output_path = os.path.join(output_dir, output_filename)
    
    if STABILITY_API_KEY:
        print(f"[INFO] Engine: Stable Diffusion XL (Core)")
        print(f"[INFO] Generating High-Quality Image...")
        
        try:
            # Stability AI API - Text to Image
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            body = {
                "steps": 40,
                "width": 1024,
                "height": 1024,
                "seed": 0,
                "cfg_scale": 5,
                "samples": 1,
                "text_prompts": [
                    {
                        "text": "flat vector logo of " + prompt + ", minimal, solid colors, thick lines, simple, clean geometric shapes, white background, professional vector art, no gradients, no shading, adobe illustrator style",
                        "weight": 1
                    },
                    {
                        "text": "3d render, realistic, photography, shadows, gradients, noise, texture, blurry, pixelated, grain, watermark, complex details, sketch, thin lines",
                        "weight": -1
                    }
                ],
            }
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {STABILITY_API_KEY}",
            }
            
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code != 200:
                print(f"[ERROR] Stability API Error: {response.status_code}")
                # print(response.text) # Debug only
            else:
                data = response.json()
                for i, image in enumerate(data["artifacts"]):
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(image["base64"]))
                    print(f"[SUCCESS] Image saved to: {output_path}")
                    return output_path
                    
        except Exception as e:
            print(f"[ERROR] Stability Generation Failed: {e}")
            
    else:
        print("[WARN] Stability API Key not found in .env")

    # Fallback to local user action if API fails
    print(f"[FAIL] Generation failed.")
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_image_nanobanana(sys.argv[1])
