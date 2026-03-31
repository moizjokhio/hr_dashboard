const SESSION_SECRET = "hr-analytics-admin-session-secret-v1";

export const AUTH_COOKIE_NAME = "admin_session";
export const ADMIN_USERNAME = "admin";
export const ADMIN_PASSWORD = "Admin@HR2026!Secure";

const encoder = new TextEncoder();

function toBase64UrlFromBytes(bytes: Uint8Array): string {
  if (typeof Buffer !== "undefined") {
    return Buffer.from(bytes)
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/g, "");
  }

  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }

  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function fromBase64UrlToBytes(value: string): Uint8Array {
  if (typeof Buffer !== "undefined") {
    const base64 = value.replace(/-/g, "+").replace(/_/g, "/");
    const padded = `${base64}${"=".repeat((4 - (base64.length % 4)) % 4)}`;
    return new Uint8Array(Buffer.from(padded, "base64"));
  }

  const base64 = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = `${base64}${"=".repeat((4 - (base64.length % 4)) % 4)}`;
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);

  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }

  return bytes;
}

function constantTimeEqual(a: string, b: string): boolean {
  const aBytes = encoder.encode(a);
  const bBytes = encoder.encode(b);
  const maxLength = Math.max(aBytes.length, bBytes.length);
  let mismatch = aBytes.length === bBytes.length ? 0 : 1;

  for (let i = 0; i < maxLength; i += 1) {
    const aValue = i < aBytes.length ? aBytes[i] : 0;
    const bValue = i < bBytes.length ? bBytes[i] : 0;
    mismatch |= aValue ^ bValue;
  }

  return mismatch === 0;
}

async function sign(payloadB64: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(SESSION_SECRET),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(payloadB64));
  return toBase64UrlFromBytes(new Uint8Array(signature));
}

export async function validateAdminCredentials(
  username: string,
  password: string
): Promise<boolean> {
  return constantTimeEqual(username, ADMIN_USERNAME) && constantTimeEqual(password, ADMIN_PASSWORD);
}

export async function createSessionToken(username: string): Promise<string> {
  const exp = Math.floor(Date.now() / 1000) + 60 * 60 * 8;
  const payload = JSON.stringify({ u: username, exp });
  const payloadB64 = toBase64UrlFromBytes(encoder.encode(payload));
  const sigB64 = await sign(payloadB64);
  return `${payloadB64}.${sigB64}`;
}

export async function verifySessionToken(token: string | undefined): Promise<{ username: string } | null> {
  if (!token) {
    return null;
  }

  const [payloadB64, sigB64] = token.split(".");
  if (!payloadB64 || !sigB64) {
    return null;
  }

  const expectedSig = await sign(payloadB64);
  if (!constantTimeEqual(sigB64, expectedSig)) {
    return null;
  }

  try {
    const payloadBytes = fromBase64UrlToBytes(payloadB64);
    const payloadText = new TextDecoder().decode(payloadBytes);
    const payload = JSON.parse(payloadText) as { u?: string; exp?: number };

    if (!payload.u || !payload.exp || payload.exp <= Math.floor(Date.now() / 1000)) {
      return null;
    }

    return { username: payload.u };
  } catch {
    return null;
  }
}
