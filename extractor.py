import json
import subprocess

class Extractor:
    def __init__(self, model="qwen3.5:0.8b"):
        self.model = model
    
    def extract(self, thesis):
        """Send thesis to small model, return T, M, IST"""
        
        prompt = f"""Extract from the following thesis three things:

1. Target (T): what specific entity is being acted upon? (e.g., "steel vessel", "car", "art project")

2. Mechanism (M): how is the target being affected? (e.g., "applying pressure", "purchasing", "researching")

3. Permanent outcome (IST): a permanent, one-way change to the target that cannot be undone through normal means. Examples: "rupture", "destruction", "permanent deformation". Non-examples: "ownership" (you can sell a car), "completion" (an art project can be revised).

Thesis: {thesis}

Return ONLY JSON: {{"T": "...", "M": "...", "IST": "..."}} Use "unknown" if unclear."""
        
        print("   Thinking... (may take 10-30 seconds on CPU)", end="", flush=True)
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True, text=True, timeout=60,
                encoding="utf-8"  # Force UTF-8 decoding
            )
            print("\r   Done.                    ", flush=True)
            
            output = result.stdout.strip()
            
            # Parse JSON from output
            start = output.find('{')
            end = output.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = output[start:end]
                data = json.loads(json_str)
                return data.get("T", "unknown"), data.get("M", "unknown"), data.get("IST", "unknown")
        except subprocess.TimeoutExpired:
            print("\r   Timeout (60 seconds). Using unknown.          ", flush=True)
        except UnicodeDecodeError as e:
            print(f"\r   Encoding error: {e}", flush=True)
            print("   Trying fallback...", flush=True)
        except Exception as e:
            print(f"\r   Error: {e}", flush=True)
        
        return "unknown", "unknown", "unknown"

