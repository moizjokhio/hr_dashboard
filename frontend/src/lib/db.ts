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

const pool = new Pool({
  connectionString: pgConnectionString,
  ssl: connectionString.includes('localhost') ? false : {
    rejectUnauthorized: false,
  },
});

export default pool;
