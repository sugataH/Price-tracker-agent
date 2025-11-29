# backend/app/ai/agent.py
import os
import json
import asyncio

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

try:
    from groq import Groq
except Exception:
    Groq = None

async def _fallback_aggregate(scraped_results):
    prices = [r.get("price") for r in scraped_results if isinstance(r.get("price"), (int, float))]
    final_price = min(prices) if prices else None
    name = None
    for r in scraped_results:
        if r.get("name"):
            name = r.get("name")
            break
    return {"price": final_price, "name": name, "status": "ok" if final_price is not None else "error", "explain": "fallback"}

async def _call_groq(scraped_results, product_name=""):
    if Groq is None or not GROQ_API_KEY:
        raise RuntimeError("Groq SDK not available or GROQ_API_KEY not set")

    def _blocking_call():
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
Extract the best realistic product price and a clean product name from the following scraped results.
Return only JSON with keys: price (number|null), name (string|null), status ('ok'|'error'), explain (string).
Product name (user): {product_name}
Scraped results:
{json.dumps(scraped_results, default=str)}
"""
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role":"system","content":"You are a price extraction assistant."},
                      {"role":"user","content":prompt}],
            temperature=0.0,
            max_tokens=400
        )
        try:
            text = resp.choices[0].message["content"]
        except Exception:
            text = resp.choices[0].message.content if hasattr(resp.choices[0].message, "content") else str(resp)
        return text

    try:
        text = await asyncio.to_thread(_blocking_call)
        parsed = json.loads(text.strip())
        price = parsed.get("price")
        if isinstance(price, str):
            try:
                price = float(price.replace("₹", "").replace(",", "").strip())
            except Exception:
                price = None
        return {"price": price, "name": parsed.get("name"), "status": parsed.get("status", "ok" if price is not None else "error"), "explain": parsed.get("explain", "from_groq")}
    except Exception as e:
        print("Groq call failed:", e)
        return await _fallback_aggregate(scraped_results)

async def ai_validate_price(product_name_or_results, scraped_results=None):
    if scraped_results is None:
        scraped = product_name_or_results if isinstance(product_name_or_results, list) else []
        product_name = ""
    else:
        product_name = product_name_or_results or ""
        scraped = scraped_results or []

    if GROQ_API_KEY and Groq is not None:
        try:
            return await _call_groq(scraped, product_name)
        except Exception as e:
            print("Groq error, falling back:", e)
            return await _fallback_aggregate(scraped)
    else:
        return await _fallback_aggregate(scraped)
