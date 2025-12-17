const API_URL = "http://127.0.0.1:5000";

export async function getFunds() {
  const url = `${API_URL}/api/funds`;
  console.log("👉 Fetching URL:", url);

  const res = await fetch(url, {
    cache: "no-store",
  });

  console.log("👉 Response status:", res.status);

  const data = await res.json();
  console.log("👉 Full API response:", data);

  // ✅ THIS IS THE KEY LINE
  return Array.isArray(data.funds) ? data.funds : [];
}
