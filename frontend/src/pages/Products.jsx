import { useEffect, useState } from "react";
import { fetchProducts, addProduct } from "../api/products";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [inputUrl, setInputUrl] = useState("");

  useEffect(() => {
    loadProducts();
  }, []);

  async function loadProducts() {
    try {
      const data = await fetchProducts();
      setProducts(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleAddProduct() {
    if (!inputUrl.trim()) return;

    try {
      await addProduct({ url: inputUrl });
      setInputUrl("");
      loadProducts();
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Tracked Products</h1>

      <div style={{ marginBottom: 20 }}>
        <input
          type="text"
          value={inputUrl}
          placeholder="Enter product URL"
          onChange={(e) => setInputUrl(e.target.value)}
          style={{ padding: 8, width: 300, marginRight: 10 }}
        />
        <button onClick={handleAddProduct}>Add Product</button>
      </div>

      <ul>
        {products.map((p) => (
          <li key={p.id}>
            {p.url} — ₹{p.price}
          </li>
        ))}
      </ul>
    </div>
  );
}
