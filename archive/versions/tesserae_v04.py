import json
import os
from datetime import datetime
from clm import CLM
from extractor import Extractor

class Tesserae:
    def __init__(self, lang="english"):
        self.lang = lang
        self.strings = {}
        self.current_string = None
        self._load_concepts()
        self._load_strings()
    
    def _load_concepts(self):
        with open("shell.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.concepts = data["concepts"]
            self.suchness_buckets = data.get("suchness_buckets", {})
    
    def _load_strings(self):
        with open(f"strings/{self.lang}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            self.ui_strings = data["ui"]
            self.concept_mappings = data["concept_mappings"]
    
    def get_ui(self, key):
        return self.ui_strings.get(key, key)
    
    def get_concept_label(self, concept_id):
        return self.concept_mappings.get(str(concept_id), f"Concept {concept_id}")
    
    def get_icon(self, concept_id):
        return self.concepts.get(str(concept_id), {}).get("default_icon", "❓")
    
    def create_mixtape(self, name):
        string_id = str(len(self.strings) + 1)
        self.strings[string_id] = {
            "id": string_id,
            "name": name,
            "invariants": [],
            "constraints": [],
            "tradeoffs": [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "language": self.lang
        }
        self.current_string = string_id
        return string_id
    
    def switch_mixtape(self, string_id):
        if string_id in self.strings:
            self.current_string = string_id
            return True
        return False
    
    def add_statement(self, text, concept_id):
        if not self.current_string:
            return False
        
        entry = {"text": text, "timestamp": datetime.now().isoformat()}
        mixtape = self.strings[self.current_string]
        
        if concept_id == "1":
            mixtape["invariants"].append(entry)
        elif concept_id == "2":
            mixtape["constraints"].append(entry)
        elif concept_id == "3":
            mixtape["tradeoffs"].append(entry)
        else:
            return False
        
        mixtape["modified"] = datetime.now().isoformat()
        return True
    
    def get_current_mixtape(self):
        if self.current_string:
            return self.strings[self.current_string]
        return None
    
    def list_mixtapes(self):
        return [(sid, data["name"]) for sid, data in self.strings.items()]
    
    def save_mixtape(self, filename):
        if self.current_string and self.current_string in self.strings:
            data = {self.current_string: self.strings[self.current_string]}
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"Error saving: {e}")
                return False
        return False
    
    def load_mixtape(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for string_id, string_data in data.items():
                        self.strings[string_id] = string_data
                        self.current_string = string_id
                return True
            except Exception as e:
                print(f"Error loading: {e}")
                return False
        return False


def main():
    print("=== Tesserae v0.4 ===")
    print("CLM gate active — theses are checked for safety")
    print()
    
    lang = input("Select language (english/telugu): ").strip().lower()
    if lang not in ["english", "telugu"]:
        print("Defaulting to english")
        lang = "english"
    
    t = Tesserae(lang=lang)
    extractor = Extractor()
    
    if os.path.exists("tesserae_save.json"):
        t.load_mixtape("tesserae_save.json")
        print(t.get_ui("loaded"))
    
    while True:
        print(f"\n{t.get_ui('menu_title')}")
        print(t.get_ui("menu_create_mixtape"))
        print(t.get_ui("menu_switch_mixtape"))
        print(t.get_ui("menu_add_statement"))
        print(t.get_ui("menu_show_map"))
        print(t.get_ui("menu_save"))
        print(t.get_ui("menu_load"))
        print(t.get_ui("menu_exit"))
        
        choice = input("Choice: ").strip()
        
        if choice == "1":
            # Step 1: Thesis extraction (using small model)
            thesis = input(t.get_ui("clm_prompt_thesis"))
            clm = CLM(lang=t.lang)
            extracted = clm.extract_with_model(thesis, extractor)
            
            # Validate extraction is meaningful
            if not clm.is_meaningful():
                print("CLM could not extract a clear target or irreversible outcome.")
                print("Please rephrase your thesis more specifically.")
                continue
            
            # Step 2: User confirmation
            while True:
                print(t.get_ui("clm_review_thesis").format(
                    T=extracted["T"],
                    M=extracted["M"],
                    IST=extracted["IST"]
                ))
                confirm = input().strip().lower()
                
                if confirm == "yes":
                    break
                elif confirm == "edit":
                    thesis = input(t.get_ui("clm_edit_thesis"))
                    extracted = clm.extract_with_model(thesis, extractor)
                else:
                    print(t.get_ui("clm_error_no_thesis"))
                    return
            
            # Step 3: Layer 1 evaluation
            if clm.check_pt_to_ist():
                print(t.get_ui("clm_refusal"))
                return
            
            # Step 4: PASS — proceed
            print(t.get_ui("clm_pass"))
            constraints = input(t.get_ui("clm_constraints"))
            
            # Create the mixtape
            name = input(t.get_ui("prompt_mixtape_name"))
            t.create_mixtape(name)
            print(f"Mixtape '{name}' created.")
        
        elif choice == "2":
            mixtapes = t.list_mixtapes()
            if not mixtapes:
                print(t.get_ui("error_no_mixtape"))
                continue
            print("\nMixtapes:")
            for sid, name in mixtapes:
                print(f"  {sid}: {name}")
            sid = input("ID: ").strip()
            if t.switch_mixtape(sid):
                print(f"Switched to {t.get_current_mixtape()['name']}")
            else:
                print(t.get_ui("error_invalid_choice"))
        
        elif choice == "3":
            if not t.get_current_mixtape():
                print(t.get_ui("error_no_mixtape"))
                continue
            text = input(t.get_ui("prompt_statement"))
            print(f"  1: {t.get_icon('1')} {t.get_concept_label('1')}")
            print(f"  2: {t.get_icon('2')} {t.get_concept_label('2')}")
            print(f"  3: {t.get_icon('3')} {t.get_concept_label('3')}")
            concept = input(t.get_ui("prompt_concept"))
            if concept in ["1", "2", "3"] and t.add_statement(text, concept):
                print(t.get_ui("added"))
            else:
                print(t.get_ui("error_invalid_choice"))
        
        elif choice == "4":
            mixtape = t.get_current_mixtape()
            if not mixtape:
                print(t.get_ui("error_no_mixtape"))
                continue
            print(f"\n--- {mixtape['name']} ---")
            for concept_id, items in [
                ("1", mixtape["invariants"]),
                ("2", mixtape["constraints"]),
                ("3", mixtape["tradeoffs"])
            ]:
                icon = t.get_icon(concept_id)
                label = t.get_concept_label(concept_id)
                print(f"\n{icon} {label}:")
                if items:
                    for item in items:
                        print(f"  - {item['text']}")
                else:
                    print("  (none)")
        
        elif choice == "5":
            filename = input(t.get_ui("prompt_filename"))
            if t.save_mixtape(filename):
                print(t.get_ui("saved"))
            else:
                print(t.get_ui("error_no_mixtape"))
        
        elif choice == "6":
            filename = input(t.get_ui("prompt_filename"))
            if t.load_mixtape(filename):
                print(t.get_ui("loaded"))
            else:
                print("File not found or invalid.")
        
        elif choice == "7":
            t.save_mixtape("tesserae_save.json")
            print(t.get_ui("saved"))
            print("Goodbye!")
            break
        
        else:
            print(t.get_ui("error_invalid_choice"))


if __name__ == "__main__":
    main()


