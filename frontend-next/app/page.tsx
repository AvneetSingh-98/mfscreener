import { getFunds } from "@/lib/api";

export default async function HomePage() {
  const funds = await getFunds();

  console.log("👉 Funds received in page:", funds);

  return (
    <div style={{ padding: 24 }}>
      <h1>Large Cap Mutual Fund Screener</h1>

      <pre style={{ background: "#eee", padding: 12 }}>
        {JSON.stringify(funds, null, 2)}
      </pre>

      {funds.length === 0 ? (
        <p>No funds found.</p>
      ) : (
        <table border={1} cellPadding={8}>
          <thead>
            <tr>
              <th>Fund Name</th>
              <th>AMC</th>
              <th>Category</th>
            </tr>
          </thead>
          <tbody>
            {funds.map((fund: any) => (
              <tr key={fund.fund_id}>
                <td>{fund.name}</td>
                <td>{fund.amc}</td>
                <td>{fund.category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}


