import type { VercelRequest, VercelResponse } from "@vercel/node";

export default function handler(
  req: VercelRequest,
  res: VercelResponse,
) {
  // Set CORS headers only for this endpoint
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "*");

  // Handle OPTIONS preflight request
  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }

  // Handle GET request
  if (req.method === "GET") {
    res.status(200).json({ status: "ok" });
    return;
  }

  // Method not allowed
  res.status(405).json({ error: "Method not allowed" });
}

