export const API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchProducts() {
  const response = await fetch(`${API_BASE_URL}/products/`);
  if (!response.ok) {
    throw new Error("Failed to fetch products");
  }
  return await response.json();
}

export async function addProduct(data) {
  const response = await fetch(`${API_BASE_URL}/products/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to add product");
  }

  return await response.json();
}
