import re

class CLM:
    def __init__(self, lang="english"):
        self.lang = lang
        self.thesis = None
        self.T = None   # Target
        self.M = None   # Mechanism
        self.IST = None # Irreversible Structural Transition

    def extract_with_model(self, thesis, extractor):
        T, M, IST = extractor.extract(thesis)
        self.T = T
        self.M = M
        self.IST = IST
        return {"T": T, "M": M, "IST": IST}  
    
    def extract_thesis(self, user_input):
        """Extract T, M, IST using keyword patterns + heuristics"""
        # v0.3: Simple keyword matching
        # Future: LLM-assisted extraction
        
        # Default: assume user input is the thesis
        thesis = user_input.strip()
        
        # Simple extraction (expandable)
        # Look for patterns like "how to X Y" or "what is the minimum Z to W"
        self.thesis = thesis
        
        # Placeholder extraction (user will confirm)
        self.T = self._extract_target(user_input)
        self.M = self._extract_mechanism(user_input)
        self.IST = self._extract_ist(user_input)
        
        return {
            "thesis": self.thesis,
            "T": self.T,
            "M": self.M,
            "IST": self.IST
        }
    
    def _extract_target(self, text):
        """Extract target entity (steel vessel, car, system, etc.)"""
        # v0.3: Simple noun phrase extraction
        # Look for patterns like "rupture a [target]" or "pressure on [target]"
        patterns = [
            r"rupture a ([^.,!?]+)",
            r"pressure (?:on|in) a ([^.,!?]+)",
            r"damage to ([^.,!?]+)",
            r"failure of ([^.,!?]+)",
            r"configure ([^.,!?]+) to",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        return "unknown_target"
    
    def _extract_mechanism(self, text):
        """Extract mechanism (pressure increase, configuration, etc.)"""
        patterns = [
            r"minimum pressure (?:required|to|for)",
            r"configure (?:components|settings) to cause",
            r"(?:increase|apply) (?:pressure|force|stress)",
        ]
        for pattern in patterns:
            if re.search(pattern, text.lower()):
                return "pressure_increase"  # placeholder
        return "unknown_mechanism"
    
    def _extract_ist(self, text):
        """Extract irreversible structural transition (rupture, failure, etc.)"""
        ist_keywords = ["rupture", "failure", "damage", "break", "destroy", "collapse", "overpressure"]
        for keyword in ist_keywords:
            if keyword in text.lower():
                return keyword
        return "unknown_ist"
    
    def check_pt_to_ist(self):
        """Evaluate whether response would increase Path Traversability toward IST"""
        # v0.3: Simple keyword-based detection
        # Future: More sophisticated LLM-based evaluation
        
        # Dangerous keywords that indicate optimization toward failure
        dangerous = [
            "minimum", "threshold", "maximum", "limit",
            "optimize", "compress", "bypass", "override",
            "sequence", "step", "procedure", "instructions"
        ]
        
        # Check if T, M, IST are all present and specific
        if self.T and self.T != "unknown_target" and self.T != "general class":
            if self.IST and self.IST in ["rupture", "failure", "damage", "break", "collapse", "overpressure"]:
                # Check for optimization language
                for word in dangerous:
                    if word in self.thesis.lower():
                        return True  # FAIL — PT→IST detected
                # Also check if target is specific (not general)
                if self.T not in ["vessel", "system", "component", "structure"]:
                    return True  # FAIL — specific target + IST = PT→IST
        return False  # PASS
    
    def refuse(self, ui_getter):
        """Return refusal message in user's language"""
        return ui_getter("clm_refusal")
    
    def pass_message(self, ui_getter):
        """Return pass message in user's language"""
        return ui_getter("clm_pass")

    def is_meaningful(self):
        """Return True if extraction has a specific target and IST"""
        if self.T == "unknown_target" or self.T == "general class":
            return False
        if self.IST == "unknown_ist":
            return False
        return True
        

