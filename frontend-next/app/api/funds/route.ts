import { NextResponse } from "next/server";
import { MongoClient } from "mongodb";

const MONGO_URI = process.env.MONGO_URI!;
const DB_NAME = "mfscreener";

let client: MongoClient;

async function getClient() {
  if (!client) {
    client = new MongoClient(MONGO_URI);
    await client.connect();
  }
  return client;
}

export async function GET() {
  try {
    const client = await getClient();
    const db = client.db(DB_NAME);

    const funds = await db
      .collection("fund_master_v2")
      .find({})
      .project({ _id: 0 })
      .toArray();

    return NextResponse.json(funds);
  } catch (err) {
    console.error("API /funds error:", err);
    return NextResponse.json(
      { error: "Failed to fetch funds" },
      { status: 500 }
    );
  }
}
