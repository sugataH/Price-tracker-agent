# backend/app/services/secondary_checker.py
from difflib import SequenceMatcher
from typing import List, Dict

def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

class SecondaryChecker:
    """
    Confirm scraped product across multiple sites to avoid false alerts.
    """

    def verify(self, structured: Dict, scraped_results: List[Dict], name_threshold: float = 0.68, price_tolerance: float = 0.08):
        structured_name = structured.get("name") or structured.get("product_name") or ""
        structured_price = structured.get("price") or structured.get("final_price") or structured.get("current_price")

        matches = []
        confirmed = False
        best_match = None
        best_score = -1.0

        for r in scraped_results:
            r_name = r.get("name") or ""
            r_price = r.get("price")

            name_score = _similarity(structured_name, r_name)
            price_ok = False
            if structured_price is not None and r_price is not None:
                if structured_price == 0:
                    price_ok = False
                else:
                    rel_diff = abs(structured_price - r_price) / max(abs(structured_price), 1e-9)
                    price_ok = rel_diff <= price_tolerance

            overall = (name_score * 0.7) + ((1.0 if price_ok else 0.0) * 0.3)

            if name_score >= name_threshold:
                matches.append({"result": r, "name_score": name_score, "price_ok": price_ok, "score": overall})
                if overall > best_score:
                    best_score = overall
                    best_match = r
                if price_ok:
                    confirmed = True

        return {"confirmed": confirmed, "best_match": best_match, "matches": matches}
