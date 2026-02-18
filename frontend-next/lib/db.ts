import { MongoClient } from "mongodb";

const MONGO_URI = process.env.MONGO_URI!;
const DB_NAME = "mfscreener";

let client: MongoClient;

export async function getDb() {
  if (!client) {
    client = new MongoClient(MONGO_URI);
    await client.connect();
  }
  return client.db(DB_NAME);
}

