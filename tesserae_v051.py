import json
import os
from datetime import datetime

class Tesserae:
    def __init__(self, lang="english", voice=False):
        self.lang = lang
        self.voice = voice
        self.domain = "Car Purchase"
        self.budget = None
        self.must_haves = []
        self.preferences = []
        self.tensions = []
        self.candidates = []
        self.eliminated = []
        self._load_strings()
    
    def _load_strings(self):
        """Load language skins"""
        try:
            with open(f"strings/{self.lang}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.ui = data["ui"]
        except:
            self.ui = self._fallback_strings()
    
    def _fallback_strings(self):
        return {
            "welcome": "Accessible structure to think, decide, or create.",
            "domain_prompt": "Select domain:",
            "domain_car": "1. Car Purchase (available)",
            "domain_free": "2. Free Inquiry / Project (coming soon)",
            "domain_art": "3. Art Project (coming soon)",
            "budget_q": "First, what's your budget?",
            "budget_confirm": "Budget: under ${}",
            "budget_eliminate": "Eliminates about 60% of SUVs",
            "must_have_q": "What must you have? (e.g., SUV, hybrid, AWD. Type 'done' when finished)",
            "must_have_add": "Added must-have: {}",
            "must_have_eliminate": "Eliminated {} vehicles",
            "tension_q": "Any tensions you're worried about? (e.g., tech vs. reliability. Type 'done' when finished)",
            "tension_add": "Tension noted: {}",
            "tension_help": "Consider: {}",
            "choice_q": "Which feels heavier — {} or {}?",
            "choice_response": "Noted: {} heavier",
            "remaining": "Remaining candidates: {}",
            "compare_prompt": "Type 'compare' to see side-by-side, 'add' to add more constraints, or 'discover' to search.",
            "goodbye": "Goodbye."
        }
    
    def get_ui(self, key):
        return self.ui.get(key, key)
    
    def speak(self, text):
        """If voice mode enabled, simulate TTS (placeholder for actual TTS)"""
        print(text)
        if self.voice:
            # Placeholder for text-to-speech
            pass
    
    def run(self):
        self.speak(self.get_ui("welcome"))
        print()
        
        # Domain selection
        print(self.get_ui("domain_prompt"))
        print(self.get_ui("domain_car"))
        print(self.get_ui("domain_free"))
        print(self.get_ui("domain_art"))
        choice = input("\nChoice: ").strip()
        if choice != "1":
            print("Only Car Purchase is available in this version.")
            return
        
        print(f"\nDomain: {self.domain}\n")
        
        # Step 1: Budget
        self.speak(self.get_ui("budget_q"))
        budget_input = input("> ").strip()
        try:
            self.budget = int(budget_input.replace("$", "").replace(",", ""))
        except:
            self.budget = 22000
        self.speak(self.get_ui("budget_confirm").format(self.budget))
        self.speak(self.get_ui("budget_eliminate"))
        print()
        
        # Step 2: Must-haves
        self.speak(self.get_ui("must_have_q"))
        while True:
            inp = input("> ").strip().lower()
            if inp == "done":
                break
            if inp:
                self.must_haves.append(inp)
                self.speak(self.get_ui("must_have_add").format(inp))
                self.speak(self.get_ui("must_have_eliminate"))
        print()
        
        # Step 3: Tensions
        self.speak(self.get_ui("tension_q"))
        while True:
            inp = input("> ").strip()
            if inp == "done":
                break
            if inp:
                self.tensions.append(inp)
                self.speak(self.get_ui("tension_add").format(inp))
        print()
        
        # Step 4: Resolve tensions (if any)
        if self.tensions:
            for tension in self.tensions:
                # Simple parsing: "tech vs. reliability" -> ["tech", "reliability"]
                parts = tension.lower().split(" vs. ")
                if len(parts) == 2:
                    a, b = parts[0], parts[1]
                    self.speak(self.get_ui("choice_q").format(a, b))
                    choice = input("> ").strip().lower()
                    if choice in [a, b]:
                        self.speak(self.get_ui("choice_response").format(choice))
                        # Store preference for later candidate ranking
                        if hasattr(self, 'preferences'):
                            self.preferences.append(choice)
        print()
        
        # Step 5: Show remaining candidates (mock data)
        base_candidates = ["CR-V", "CX-5", "Forester", "Rogue", "Tucson", "Sportage", "RAV4"]
        remaining = self._filter_candidates(base_candidates)
        self.speak(self.get_ui("remaining").format(", ".join(remaining)))
        print()
        
        # Step 6: Next steps
        self.speak(self.get_ui("compare_prompt"))
        
        # Simple command loop
        while True:
            cmd = input("\n> ").strip().lower()
            if cmd == "exit":
                self.speak(self.get_ui("goodbye"))
                break
            elif cmd == "compare":
                self._compare_candidates(remaining)
            elif cmd == "add":
                self.speak(self.get_ui("must_have_q"))
                inp = input("> ").strip()
                if inp:
                    self.must_haves.append(inp)
                    self.speak(self.get_ui("must_have_add").format(inp))
                    remaining = self._filter_candidates(base_candidates)
                    self.speak(self.get_ui("remaining").format(", ".join(remaining)))
            elif cmd == "discover":
                self.speak("Discovery coming soon. For now, check CarGurus or CarMax.")
            else:
                self.speak("Unknown command. Try 'compare', 'add', 'discover', or 'exit'.")
    
    def _filter_candidates(self, candidates):
        """Simple filtering based on must-haves (mock implementation)"""
        # This is a mock. Real version would use actual vehicle database.
        if "hybrid" in self.must_haves:
            candidates = ["CR-V hybrid", "RAV4 hybrid", "Tucson hybrid"]
        elif "suv" in self.must_haves:
            candidates = [c for c in candidates if c in ["CR-V", "CX-5", "Forester", "Rogue", "Tucson", "Sportage", "RAV4"]]
        # Budget filter
        if self.budget and self.budget < 25000:
            candidates = [c for c in candidates if c not in ["Rogue", "Sportage"]]
        return candidates
    
    def _compare_candidates(self, candidates):
        """Mock comparison"""
        if not candidates:
            print("No candidates to compare.")
            return
        print("\n--- Comparison ---")
        for c in candidates:
            print(f"\n{c}:")
            if c == "CR-V hybrid":
                print("  Price: ~$24k")
                print("  MPG: 38")
                print("  Tech: basic")
                print("  Reliability: high")
            elif c == "RAV4 hybrid":
                print("  Price: ~$25k")
                print("  MPG: 40")
                print("  Tech: advanced")
                print("  Reliability: high")
            elif c == "Tucson hybrid":
                print("  Price: ~$23k")
                print("  MPG: 37")
                print("  Tech: most")
                print("  Reliability: medium")
            else:
                print("  Details coming soon.")


def main():
    import sys
    
    voice = "--voice" in sys.argv
    
    print("=== Tesserae v0.5.1 ===")
    lang = input("Select language (english/telugu): ").strip().lower()
    if lang not in ["english", "telugu"]:
        lang = "english"
    
    t = Tesserae(lang=lang, voice=voice)
    t.run()


if __name__ == "__main__":
    main()

