import requests, json, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class AIScrapingAgent:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.html = ""

    def analyze_target(self):
        """Step 1: Target web application ko analyze karo"""
        print(f"[+] Analyzing: {self.url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(self.url, headers=headers, timeout=15)
        self.html = res.text
        self.soup = BeautifulSoup(self.html, 'lxml')
        print(f"[+] Page Title: {self.soup.title.text.strip() if self.soup.title else 'N/A'}")
        print(f"[+] Total Tags: {len(self.soup.find_all())}")
        return True

    def detect_structure(self):
        """Step 2: DOM structure samjho - Tables, Lists, Cards"""
        structure = {
            "tables": len(self.soup.find_all("table")),
            "lists": len(self.soup.find_all(["ul", "ol"])),
            "cards": len(self.soup.find_all("div", class_=re.compile("card|product|item|post"))),
            "links": len(self.soup.find_all("a", href=True)),
            "images": len(self.soup.find_all("img")),
            "forms": len(self.soup.find_all("form")),
            "has_pagination": bool(self.soup.find(string=re.compile("Next|Load More|Pagination", re.I))),
            "is_dynamic": "react" in self.html.lower() or "__NEXT_DATA__" in self.html or "vue" in self.html.lower()
        }
        print("[+] Structure Detected:", structure)
        return structure

    def generate_rules(self):
        """Step 3: AI Agent - Structured Scraping Rules Generate karo"""
        # Smart selector detection - Client ki main requirement
        rules = {
            "target_url": self.url,
            "agent_version": "1.0",
            "extraction_rules": [],
            "pagination": {},
            "handling": {
                "retry": 3,
                "dynamic_content": "Use Playwright if is_dynamic=True",
                "rate_limit": "1 sec delay"
            }
        }

        # Rule 1: Headings
        if self.soup.find("h1"):
            rules["extraction_rules"].append({
                "field": "title",
                "selector": "h1",
                "type": "text",
                "required": True
            })
        # Rule 2: Product / Card pattern
        for tag in self.soup.find_all(["article", "div"], class_=re.compile("card|product|item"))[:1]:
            rules["extraction_rules"].append({
                "field": "items",
                "selector": f"{tag.name}.{tag.get('class')[0]}",
                "type": "list",
                "sub_fields": [
                    {"field": "name", "selector": "h2, h3, .title", "type": "text"},
                    {"field": "price", "selector": ".price, [class*=price]", "type": "text"},
                    {"field": "link", "selector": "a", "type": "attribute:href"},
                    {"field": "image", "selector": "img", "type": "attribute:src"}
                ]
            })
        # Rule 3: Tables
        if self.soup.find("table"):
            rules["extraction_rules"].append({
                "field": "table_data",
                "selector": "table tr",
                "type": "table",
                "columns": "auto-detect th"
            })

        # Rule 4: Pagination
        next_link = self.soup.find("a", string=re.compile("Next", re.I))
        if next_link:
            rules["pagination"] = {
                "type": "click_next",
                "selector": "a:-soup-contains('Next')",
                "next_url": urljoin(self.url, next_link.get("href", ""))
            }

        # Save JSON - Client ko yehi chahiye tha
        with open("scraping_rules.json", "w") as f:
            json.dump(rules, f, indent=2)
        print("[+] Rules Generated -> scraping_rules.json")
        return rules

    def validate_rules(self, rules):
        """Step 4: Rules ko validate karo"""
        print("\n[+] Validating Rules...")
        valid = 0
        for r in rules["extraction_rules"]:
            found = self.soup.select(r["selector"])
            status = "PASS" if found else "FAIL"
            if found: valid += 1
            print(f"  {r['field']} | {r['selector']} | Found: {len(found)} | {status}")
        print(f"[+] Validation: {valid}/{len(rules['extraction_rules'])} Rules Passed")
        return valid

    def run(self):
        self.analyze_target()
        struct = self.detect_structure()
        rules = self.generate_rules()
        self.validate_rules(rules)
        print("\n[DONE] Agent Complete. Use scraping_rules.json in any scraper.")
        return rules

if __name__ == "__main__":
    url = input("Target Website URL daalo: ")
    agent = AIScrapingAgent(url)
    agent.run()