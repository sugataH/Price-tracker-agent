# backend/app/ai/agent.py
import os
import json
import asyncio

# Optional: OpenAI; if not configured we fallback to a local aggregator
try:
    import openai
except Exception:
    openai = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def _fallback_aggregate(scraped_results):
    """
    Simple fallback aggregator: choose the minimum numeric price and the first name.
    Returns a dict: { "price": float|None, "name": str|None, "status": "ok"|"error", "explain": str }
    """
    prices = [r.get("price") for r in scraped_results if isinstance(r.get("price"), (int, float))]
    price = min(prices) if prices else None

    name = None
    for r in scraped_results:
        if r.get("name"):
            name = r.get("name")
            break

    status = "ok" if price is not None else "error"
    return {"price": price, "name": name, "status": status, "explain": "fallback_aggregate"}

async def ai_validate_price(product_name_or_results, scraped_results=None):
    """
    Two accepted signatures (backwards compatible):
      1) ai_validate_price(product_name: str, scraped_results: list[dict])
      2) ai_validate_price(scraped_results: list[dict])

    Returns a dict with keys:
      - price (float or None)
      - name (str or None)
      - status ("ok"|"error")
      - explain (optional)
    """
    # Normalize parameters
    if scraped_results is None:
        # signature: ai_validate_price(scraped_results)
        scraped = product_name_or_results if isinstance(product_name_or_results, list) else []
        product_name = ""
    else:
        product_name = product_name_or_results or ""
        scraped = scraped_results or []

    # If OpenAI is available and key is configured, try to call it.
    if openai and OPENAI_API_KEY:
        try:
            openai.api_key = OPENAI_API_KEY
            prompt = {
                "product_name": product_name,
                "scraped_results": scraped
            }
            # A short prompt instructing the model to return JSON
            system_msg = "You are an assistant that chooses the best realistic product price from messy scraped data. Respond only with a JSON object."
            user_msg = f"Product name: {product_name}\nScraped results (JSON array):\n{json.dumps(scraped, default=str)}\n\nReturn JSON with keys: price (number|null), name (string|null), status ('ok' or 'error'), explain (short)."

            # Use ChatCompletion if available; handle both APIs
            try:
                resp = openai.ChatCompletion.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ],
                    temperature=0.0,
                    max_tokens=400
                )
                text = resp.choices[0].message["content"]
            except Exception:
                # Fallback to completions
                resp = openai.Completion.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    prompt=user_msg,
                    max_tokens=400,
                    temperature=0.0
                )
                text = resp.choices[0].text

            # Try parse JSON
            try:
                parsed = json.loads(text.strip())
                # Ensure keys exist
                price = parsed.get("price")
                # convert to number if string
                if isinstance(price, str):
                    try:
                        price = float(price.replace(",", "").replace("₹", "").strip())
                    except Exception:
                        price = None
                return {
                    "price": price,
                    "name": parsed.get("name"),
                    "status": parsed.get("status", "ok" if price is not None else "error"),
                    "explain": parsed.get("explain", "from_llm")
                }
            except Exception:
                # LLM returned non-JSON: try to extract a number
                # fallback to aggregator
                return await _fallback_aggregate(scraped)
        except Exception as e:
            # LLM call failed; fallback
            print("⚠ AI agent call failed:", e)
            return await _fallback_aggregate(scraped)
    else:
        # No OpenAI configured: fallback aggregator
        return await _fallback_aggregate(scraped)
