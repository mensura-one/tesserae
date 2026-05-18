import json
import os
from datetime import datetime

class Tesserae:
    def __init__(self, lang="english"):
        self.lang = lang
        self.concepts = self._load_concepts()
        self.current_string = None
        self.strings = {}  # id -> string data
        
    def _load_concepts(self):
        import json
        with open("concepts.json", "r",
    encoding="utf-8") as f:
            data = json.load(f)
            return data["concepts"]
    
    def _get_label(self, concept_id):
        return self.concepts[concept_id]["mappings"].get(
            self.lang, 
            self.concepts[concept_id]["mappings"]["english"]
        )
    
    def _get_icon(self, concept_id):
        return self.concepts[concept_id]["default_icon"]
    
    def create_string(self, name):
        string_id = str(len(self.strings) + 1)
        self.strings[string_id] = {
            "id": string_id,
            "name": name,
            "invariants": [],
            "constraints": [],
            "tradeoffs": [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        self.current_string = string_id
        return string_id
    
    def add_statement(self, text, concept_id):
        if not self.current_string:
            print("No active string. Create one first.")
            return False
        
        string = self.strings[self.current_string]
        entry = {
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        
        if concept_id == "1":
            string["invariants"].append(entry)
        elif concept_id == "2":
            string["constraints"].append(entry)
        elif concept_id == "3":
            string["tradeoffs"].append(entry)
        else:
            return False
        
        string["modified"] = datetime.now().isoformat()
        return True
    
    def show_map(self):
        if not self.current_string:
            print("No active string.")
            return
        
        string = self.strings[self.current_string]
        print(f"\n--- string: {string['name']} ---")
        
        for concept_id, items in [("1", string["invariants"]), 
                                   ("2", string["constraints"]), 
                                   ("3", string["tradeoffs"])]:
            icon = self._get_icon(concept_id)
            label = self._get_label(concept_id)
            print(f"\n{icon} {label}:")
            if items:
                for item in items:
                    print(f"  - {item['text']}")
            else:
                print("  (none)")
    
    def save(self, filename):
        with open(filename, "w",
    encoding="utf-8") as f:
                json.dump(self.strings, f,
    indent=2, ensure_ascii=False)
    
    def load(self, filename):
        import os
        if os.path.exists(filename):
            with open(filename, "r",
    encoding="utf-8") as f:
                self.strings = json.load(f)
            return True
        return False
