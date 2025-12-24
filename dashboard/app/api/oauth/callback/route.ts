import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { code, code_verifier, redirect_uri } = body;

    if (!code || !code_verifier || !redirect_uri) {
      return NextResponse.json(
        {
          error: "Missing required parameters: code, code_verifier, redirect_uri",
        },
        { status: 400 },
      );
    }

    const identityUrl = process.env.IDENTITY_URL || process.env.NEXT_PUBLIC_IDENTITY_URL;
    const clientId = process.env.IDENTITY_CLIENT_ID || process.env.NEXT_PUBLIC_IDENTITY_CLIENT_ID;

    if (!identityUrl || !clientId) {
      return NextResponse.json(
        {
          error: "Server configuration error: missing identity provider settings",
          hint: "Set IDENTITY_URL and IDENTITY_CLIENT_ID in environment variables",
        },
        { status: 500 },
      );
    }

    // Exchange code for tokens with identity provider
    const params = new URLSearchParams();
    params.set("grant_type", "authorization_code");
    params.set("code", code);
    params.set("code_verifier", code_verifier);
    params.set("redirect_uri", redirect_uri);
    params.set("client_id", clientId);

    const tokenResponse = await fetch(`${identityUrl}/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: params.toString(),
    });

    if (!tokenResponse.ok) {
      const errorText = await tokenResponse.text().catch(
        () => tokenResponse.statusText,
      );
      return NextResponse.json(
        {
          error: "Token exchange failed",
          details: errorText,
        },
        { status: tokenResponse.status },
      );
    }

    // Parse token response
    const contentType = tokenResponse.headers.get("content-type");
    let tokenData: { access_token: string; id_token?: string };

    if (contentType?.includes("application/json")) {
      tokenData = await tokenResponse.json();
    } else {
      // Handle form-encoded response
      const text = await tokenResponse.text();
      const formParams = new URLSearchParams(text);
      tokenData = {
        access_token: formParams.get("access_token") || "",
        id_token: formParams.get("id_token") || undefined,
      };
    }

    if (!tokenData.access_token) {
      return NextResponse.json(
        {
          error: "Token exchange succeeded but no access_token in response",
        },
        { status: 500 },
      );
    }

    // Return tokens to frontend
    return NextResponse.json({
      access_token: tokenData.access_token,
      id_token: tokenData.id_token,
    });
  } catch (error) {
    console.error("OAuth callback error:", error);
    return NextResponse.json(
      {
        error: "Internal server error",
        message:
          error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 },
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
