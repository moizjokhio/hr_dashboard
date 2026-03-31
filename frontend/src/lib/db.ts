import { Pool } from 'pg';

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error('DATABASE_URL is not configured for frontend server actions');
}

function buildPgConnectionString(rawUrl: string): string {
  const parsed = new URL(rawUrl);

  // pg can let URL SSL params override ssl config passed in code.
  // Remove them so our explicit ssl object is consistently applied.
  parsed.searchParams.delete('sslmode');
  parsed.searchParams.delete('sslcert');
  parsed.searchParams.delete('sslkey');
  parsed.searchParams.delete('sslrootcert');

  return parsed.toString();
}

const pgConnectionString = buildPgConnectionString(connectionString);

const isLocalDb = connectionString.includes('localhost') || connectionString.includes('127.0.0.1');

const pool = new Pool({
  connectionString: pgConnectionString,
  ssl: isLocalDb ? false : {
    rejectUnauthorized: false,
  },
  // Fail fast in dev when network DB is slow/unreachable so UI can render fallbacks.
  connectionTimeoutMillis: Number(process.env.PG_CONNECTION_TIMEOUT_MS || 5000),
  query_timeout: Number(process.env.PG_QUERY_TIMEOUT_MS || 15000),
  idleTimeoutMillis: Number(process.env.PG_IDLE_TIMEOUT_MS || 30000),
});

export default pool;
