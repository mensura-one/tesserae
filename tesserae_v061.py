class CarPurchaseGuide:
    def __init__(self):
        self.budget = None
        self.body_style = None
        self.must_haves = []
        self.tradeoff = None
        self.zip_code = None

    def print_header(self):
        print("=== Tesserae v0.6.1 – Car Purchase Guide ===\n")

    def run(self):
        self.print_header()

        # Domain selection
        print("Select domain:")
        print("1. Car Purchase")
        print("2. Project (coming soon)")
        print("3. Art Project (coming soon)")
        domain_choice = input("\nChoice: ").strip()
        if domain_choice != "1":
            print("Only Car Purchase is available in this version.")
            return

        # Step 1 – Budget
        print("\nStep 1 – Budget")
        while True:
            try:
                self.budget = int(input("Enter your maximum budget (e.g., 25000): ").strip())
                break
            except ValueError:
                print("Please enter a number (e.g., 25000).")

        # Step 2 – Body style
        print("\nStep 2 – Body style")
        print("1. SUV")
        print("2. Sedan")
        print("3. Truck")
        print("4. Hatchback")
        body_choice = input("Choice (1-4): ").strip()
        body_map = {"1": "SUV", "2": "sedan", "3": "truck", "4": "hatchback"}
        self.body_style = body_map.get(body_choice, "sedan")

        # Step 3 – Must‑haves (multiple)
        print("\nStep 3 – Must‑haves (select multiple, space‑separated)")
        print("1. Hybrid")
        print("2. AWD")
        print("3. Reliability")
        print("4. Safety")
        choices = input("Choices (e.g., 2 3): ").strip().split()
        mh_map = {"1": "hybrid", "2": "awd", "3": "reliability", "4": "safety"}
        for ch in choices:
            if ch in mh_map:
                self.must_haves.append(mh_map[ch])

        # Step 4 – Tradeoff
        print("\nStep 4 – Tradeoff (choose one)")
        print("1. Reliability matters more than tech")
        print("2. Tech matters more than reliability")
        trade_choice = input("Choice (1 or 2): ").strip()
        self.tradeoff = "reliability" if trade_choice == "1" else "tech"

        # Step 5 – Location (optional)
        print("\nStep 5 – Location (optional)")
        zip_input = input("Enter your zip code (or press Enter to skip): ").strip()
        self.zip_code = zip_input if zip_input else None

        # Generate recommendations
        recommendations = self.generate_recommendations()

        # Show summary
        self.show_summary()
        self.show_search_query(recommendations)

        # Offer adjustments
        self.offer_adjustments()

    def generate_recommendations(self):
        """Simple rule‑based recommendations (no external data)."""
        # Start with a pool of common models with attributes
        all_cars = [
            ("Honda CR-V", "SUV", 26000, True, True, True, True, 4),
            ("Toyota RAV4", "SUV", 27000, True, True, True, True, 4),
            ("Mazda CX-5", "SUV", 25000, False, True, True, True, 5),
            ("Subaru Forester", "SUV", 24000, False, True, True, True, 3),
            ("Honda Civic", "sedan", 21000, True, False, True, True, 3),
            ("Toyota Camry", "sedan", 23000, True, False, True, True, 3),
            ("Honda Accord", "sedan", 24000, True, False, True, True, 4),
            ("Toyota Corolla", "sedan", 19000, True, False, True, True, 2),
            ("Ford F-150", "truck", 35000, True, True, False, True, 4),
            ("Tesla Model 3", "sedan", 40000, False, True, True, True, 5),
            ("Hyundai Tucson", "SUV", 23000, True, True, True, True, 4),
            ("Kia Sportage", "SUV", 22000, True, True, True, True, 3),
        ]
        matches = []
        for name, bstyle, price, hybrid, awd, reliable, safe, tech in all_cars:
            if price > self.budget:
                continue
            if bstyle != self.body_style:
                continue
            if "hybrid" in self.must_haves and not hybrid:
                continue
            if "awd" in self.must_haves and not awd:
                continue
            if "reliability" in self.must_haves and not reliable:
                continue
            if "safety" in self.must_haves and not safe:
                continue
            matches.append(name)
        # Deduplicate and return top 3
        unique = []
        for m in matches:
            if m not in unique:
                unique.append(m)
        return unique[:3]

    def show_summary(self):
        print("\n" + "="*40)
        print("Your preferences:")
        print(f"  Budget: ${self.budget}")
        print(f"  Body style: {self.body_style}")
        print(f"  Must‑haves: {', '.join(self.must_haves) if self.must_haves else 'none'}")
        print(f"  Tradeoff: {self.tradeoff} > tech")
        if self.zip_code:
            print(f"  Location: {self.zip_code}")

    def show_search_query(self, recommendations):
        print("\n" + "="*40)
        if not recommendations:
            print("No exact matches found with your constraints.")
            print("Try adjusting your budget or must‑haves.")
        else:
            print("Recommended models based on your preferences:")
            for i, model in enumerate(recommendations, 1):
                print(f"  {i}. {model}")
            # Create a search query string for CarGurus/CarMax
            query = " OR ".join(recommendations[:3])
            year_range = "2020-2022"  # simple default
            print(f"\nCopy‑paste this into CarGurus / CarMax / your local search:")
            print(f'"{year_range} {query}" under ${self.budget}')

    def offer_adjustments(self):
        print("\n" + "="*40)
        adjust = input("Would you like to adjust anything? (budget, body style, must‑haves, tradeoff) [yes/no]: ").strip().lower()
        if adjust == "yes":
            print("\nRestarting the interview...")
            self.__init__()
            self.run()
        else:
            print("\nGoodbye. Happy car hunting!")

def main():
    guide = CarPurchaseGuide()
    guide.run()

if __name__ == "__main__":
    main()

