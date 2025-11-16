# by using booth.json if search name return booth number, if search booth number return name
# json structure:
#{
#    "boothName": "Dell Technologies",
#    "boothNumbers": [
#      "1827",
#      "6659",
#      "ES34"
#    ]
# }

import json
from fuzzywuzzy import process, fuzz

class Booth:
    def __init__(self, json_file='booth.json'):
        with open(json_file, 'r') as file:
            self.booth_data = json.load(file)
        # Build quick lookup for booth entries by name
        self._booth_map = {entry['boothName']: entry for entry in self.booth_data}

    # provide booth name, return booth numbers, name may typo, so use fuzzy matching, return list in best 5 matches
    def get_booth_numbers(self, booth_name):
        if not booth_name:
            return []

        booth_names = list(self._booth_map.keys())
        matches = process.extract(booth_name, booth_names, scorer=fuzz.WRatio, limit=5)
        results = []
        best_score = 0
        booth_query_lower = booth_name.lower()
        for match in matches:
            name, score = match
            # Boost score if the booth name starts with the query (handles initial words)
            if name.lower().startswith(booth_query_lower):
                score = max(score, 100)
            if score >= 60:  # threshold for fuzzy matching
                booth_entry = self._booth_map[name]
                results.append({
                    'boothName': name,
                    'boothNumbers': booth_entry['boothNumbers'],
                    'matchScore': score
                })
                best_score = max(best_score, score)

        if best_score == 100 and results:
            # Return only the best match when the top score is perfect
            results.sort(key=lambda item: item['matchScore'], reverse=True)
            return [results[0]]
        return results

    # provide booth number, return booth name
    def get_booth_name(self, booth_number):
        for booth in self.booth_data:
            if booth_number in booth['boothNumbers']:
                return booth['boothName']
        return None
    
# Example usage:
if __name__ == "__main__":
    booth = Booth()
    print(booth.get_booth_numbers("Dell Technologis"))  # Fuzzy search example
    print(booth.get_booth_name("1827"))  # Exact search example
    
    print(booth.get_booth_numbers("Tell Technologis")) 
