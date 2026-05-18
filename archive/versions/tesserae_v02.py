import json
import os
from datetime import datetime

class Tesserae:
    def __init__(self, lang_id=None):
        self.lang_id = lang_id
        self.lang_data = None
        self.strings = {}  # mixtapes: id -> {name, invariants, constraints, tradeoffs}
        self.current_string = None
        self.shell_config = None
        self.available_languages = {}
        
        self._load_shell_config()
        self._load_available_languages()
        
        if lang_id and lang_id in self.available_languages:
            self._load_language(lang_id)
        elif self.available_languages:
            # Default to first available language (prefer English if present, then Telugu)
            default = "eng" if "eng" in self.available_languages else list(self.available_languages.keys())[0]
            self._load_language(default)
    
    def _load_shell_config(self):
        """Load shell.json (IDs, suchness buckets, default icons)"""
        try:
            with open("shell.json", "r", encoding="utf-8") as f:
                self.shell_config = json.load(f)
        except FileNotFoundError:
            # Fallback shell config
            self.shell_config = {
                "version": "0.2",
                "suchness_buckets": {"western_analytic": ["eng"], "dravidian": ["tel"]},
                "concepts": {
                    "1": {"suchness": "that which must remain true", "default_icon": "🔒"},
                    "2": {"suchness": "a boundary that can bend", "default_icon": "🚧"},
                    "3": {"suchness": "a relationship between choices", "default_icon": "⚖️"}
                }
            }
    
    def _load_available_languages(self):
        """Scan strings/ and strings/community/ for all .json language skins"""
        self.available_languages = {}
        
        # Scan main strings folder
        strings_path = "strings"
        if os.path.exists(strings_path):
            for filename in os.listdir(strings_path):
                if filename.endswith(".json") and filename != "community":
                    filepath = os.path.join(strings_path, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            lang_id = data.get("language_id")
                            if lang_id:
                                self.available_languages[lang_id] = filepath
                    except Exception as e:
                        print(f"Warning: Could not load {filename}: {e}")
        
        # Scan community folder
        community_path = os.path.join(strings_path, "community")
        if os.path.exists(community_path):
            for filename in os.listdir(community_path):
                if filename.endswith(".json"):
                    filepath = os.path.join(community_path, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            lang_id = data.get("language_id")
                            if lang_id:
                                self.available_languages[lang_id] = filepath
                    except Exception as e:
                        print(f"Warning: Could not load community/{filename}: {e}")
    
    def _load_language(self, lang_id):
        """Load a specific language skin by ID"""
        if lang_id not in self.available_languages:
            return False
        
        try:
            with open(self.available_languages[lang_id], "r", encoding="utf-8") as f:
                self.lang_data = json.load(f)
                self.lang_id = lang_id
                return True
        except Exception as e:
            print(f"Error loading language {lang_id}: {e}")
            return False
    
    def get_available_languages(self):
        """Return dict of available language IDs and their names"""
        result = {}
        for lang_id, filepath in self.available_languages.items():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("language_name", lang_id)
                    result[lang_id] = name
            except:
                result[lang_id] = lang_id
        return result
    
    def get_ui(self, key):
        """Get UI string for current language"""
        if self.lang_data and "ui" in self.lang_data:
            return self.lang_data["ui"].get(key, key)
        return key
    
    def get_concept_label(self, concept_id):
        """Get concept label for current language"""
        if self.lang_data and "concept_mappings" in self.lang_data:
            return self.lang_data["concept_mappings"].get(str(concept_id), f"Concept {concept_id}")
        # Fallback to shell suchness
        return self.shell_config["concepts"].get(str(concept_id), {}).get("suchness", f"Concept {concept_id}")
    
    def get_icon(self, concept_id):
        """Get default icon for concept"""
        return self.shell_config["concepts"].get(str(concept_id), {}).get("default_icon", "❓")
    
    def get_direction(self):
        """Get text direction for current language (LTR or RTL)"""
        if self.lang_data:
            return self.lang_data.get("direction", "LTR")
        return "LTR"
    
    def get_icon_placement(self):
        """Get icon placement for current language (before or after)"""
        if self.lang_data:
            return self.lang_data.get("icon_placement", "before")
        return "before"
    
    def create_mixtape(self, name):
        """Create a new mixtape (string)"""
        string_id = str(len(self.strings) + 1)
        self.strings[string_id] = {
            "id": string_id,
            "name": name,
            "invariants": [],
            "constraints": [],
            "tradeoffs": [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "language": self.lang_id
        }
        self.current_string = string_id
        return string_id
    
    def switch_mixtape(self, string_id):
        """Switch to a different mixtape"""
        if string_id in self.strings:
            self.current_string = string_id
            return True
        return False
    
    def add_statement(self, text, concept_id):
        """Add a statement to the current mixtape"""
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
        """Get current mixtape data"""
        if self.current_string:
            return self.strings[self.current_string]
        return None
    
    def save_mixtape(self, filename):
        """Save current mixtape to a JSON file"""
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
        """Load a mixtape from a JSON file"""
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
    
    def list_mixtapes(self):
        """Return list of available mixtapes"""
        return [(sid, data["name"]) for sid, data in self.strings.items()]


def main():
    print("=== Tesserae v0.2 ===")
    print("Media player for structured thinking")
    print()
    
    # Initialize without language
    t = Tesserae()
    
    # Show available languages
    langs = t.get_available_languages()
    if not langs:
        print("No language skins found. Please ensure strings/ folder has english.json or telugu.json")
        return
    
    print("Available languages:")
    lang_list = list(langs.items())
    for i, (lang_id, lang_name) in enumerate(lang_list, 1):
        print(f"  {i}. {lang_name} ({lang_id})")
    
    # Language selection
    while True:
        try:
            choice = input("\nSelect language (number or code): ").strip().lower()
            # Try as number
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(lang_list):
                    lang_id = lang_list[idx][0]
                    break
            # Try as language code
            elif choice in langs:
                lang_id = choice
                break
            else:
                print(f"Invalid choice. Options: {', '.join(langs.keys())}")
        except:
            print("Invalid input")
    
    # Reload with selected language
    t = Tesserae(lang_id=lang_id)
    
    # Load previous save if exists
    if os.path.exists("tesserae_save.json"):
        t.load_mixtape("tesserae_save.json")
        print(t.get_ui("loaded"))
    
    # Main menu loop
    while True:
        print(f"\n{t.get_ui('menu_title')}")
        print(t.get_ui('menu_create_mixtape'))
        print(t.get_ui('menu_switch_mixtape'))
        print(t.get_ui('menu_add_statement'))
        print(t.get_ui('menu_show_map'))
        print(t.get_ui('menu_save'))
        print(t.get_ui('menu_load'))
        print(t.get_ui('menu_exit'))
        
        choice = input("Choice: ").strip()
        
        if choice == "1":
            name = input(t.get_ui('prompt_mixtape_name'))
            t.create_mixtape(name)
            print(f"Mixtape '{name}' created.")
            
        elif choice == "2":
            mixtapes = t.list_mixtapes()
            if not mixtapes:
                print("No mixtapes. Create one first.")
                continue
            print("\nMixtapes:")
            for sid, name in mixtapes:
                print(f"  {sid}: {name}")
            sid = input("ID: ").strip()
            if t.switch_mixtape(sid):
                print(f"Switched to {t.get_current_mixtape()['name']}")
            else:
                print(t.get_ui('error_invalid_choice'))
                
        elif choice == "3":
            if not t.get_current_mixtape():
                print(t.get_ui('error_no_mixtape'))
                continue
            text = input(t.get_ui('prompt_statement'))
            print(f"  1: {t.get_icon('1')} {t.get_concept_label('1')}")
            print(f"  2: {t.get_icon('2')} {t.get_concept_label('2')}")
            print(f"  3: {t.get_icon('3')} {t.get_concept_label('3')}")
            concept = input(t.get_ui('prompt_concept'))
            if concept in ["1", "2", "3"] and t.add_statement(text, concept):
                print(t.get_ui('added'))
            else:
                print(t.get_ui('error_invalid_choice'))
                
        elif choice == "4":
            mixtape = t.get_current_mixtape()
            if not mixtape:
                print(t.get_ui('error_no_mixtape'))
                continue
            print(f"\n--- {mixtape['name']} ---")
            
            for concept_id, items in [("1", mixtape["invariants"]), 
                                       ("2", mixtape["constraints"]), 
                                       ("3", mixtape["tradeoffs"])]:
                icon = t.get_icon(concept_id)
                label = t.get_concept_label(concept_id)
                print(f"\n{icon} {label}:")
                if items:
                    for item in items:
                        print(f"  - {item['text']}")
                else:
                    print("  (none)")
            
        elif choice == "5":
            filename = input(t.get_ui('prompt_filename'))
            if t.save_mixtape(filename):
                print(t.get_ui('saved'))
            else:
                print(t.get_ui('error_no_mixtape'))
                
        elif choice == "6":
            filename = input(t.get_ui('prompt_filename'))
            if t.load_mixtape(filename):
                print(t.get_ui('loaded'))
            else:
                print("File not found or invalid.")
                
        elif choice == "7":
            t.save_mixtape("tesserae_save.json")
            print(t.get_ui('saved'))
            print("Goodbye!")
            break
        else:
            print(t.get_ui('error_invalid_choice'))


if __name__ == "__main__":
    main()

