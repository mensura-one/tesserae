from tesserae import Tesserae

def main():
    print("=== Tesserae v0.1 ===")
    print("Language-agnostic structured inquiry tool")
    print()
    
    # Language selection
    lang = input("Select language (english/telugu): ").strip().lower()
    if lang not in ["english", "telugu"]:
        print("Defaulting to english")
        lang = "english"
    
    t = Tesserae(lang=lang)
    
    # Load or create
    if t.load("tesserae_save.json"):
        print("Loaded existing strings.")
    else:
        print("No saved strings found. Starting fresh.")
    
    while True:
        print("\n--- Menu ---")
        print("1. Create new string")
        print("2. Switch string")
        print("3. Add statement (🔒/🚧/⚖️)")
        print("4. Show current string map")
        print("5. Save and exit")
        
        choice = input("Choice: ").strip()
        
        if choice == "1":
            name = input("string name: ").strip()
            t.create_string(name)
            print(f"string '{name}' created.")
            
        elif choice == "2":
            print("strings:")
            for tid, string in t.strings.items():
                print(f"  {tid}: {string['name']}")
            tid = input("string ID: ").strip()
            if tid in t.strings:
                t.current_string = tid
                print(f"Switched to '{t.strings[tid]['name']}'")
            else:
                print("Invalid ID.")
                
        elif choice == "3":
            if not t.current_string:
                print("No active string. Create or switch to one first.")
                continue
                
            text = input("Your statement: ").strip()
            print("Concept:")
            print("  1: 🔒 invariant")
            print("  2: 🚧 constraint") 
            print("  3: ⚖️ tradeoff")
            concept = input("Choice (1/2/3): ").strip()
            
            if concept in ["1","2","3"]:
                if t.add_statement(text, concept):
                    print("Statement added.")
                else:
                    print("Error adding statement.")
            else:
                print("Invalid concept.")
                
        elif choice == "4":
            t.show_map()
            
        elif choice == "5":
            t.save("tesserae_save.json")
            print("Saved. Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
