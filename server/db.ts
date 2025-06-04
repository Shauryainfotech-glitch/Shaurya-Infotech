import { Pool, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-serverless';
import ws from "ws";
import * as schema from "@shared/schema";

neonConfig.webSocketConstructor = ws;

if (!process.env.DATABASE_URL) {
  throw new Error(
    "DATABASE_URL must be set. Did you forget to provision a database?",
  );
}

// Connection pool configuration
const poolConfig = {
  connectionString: process.env.DATABASE_URL,
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000, // How long a client is allowed to remain idle before being closed
  connectionTimeoutMillis: 2000, // How long to wait for a connection
  maxUses: 7500, // Close & replace a connection after it has been used this many times
};

// Create connection pool with error handling
export const pool = new Pool(poolConfig);

// Handle pool errors
pool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
});

// Handle pool connection errors
pool.on('connect', (client) => {
  client.on('error', (err) => {
    console.error('Database client error:', err);
  });
});

// Create Drizzle ORM instance with connection pool
export const db = drizzle(pool, { schema });

// Helper function to check database connection
export async function checkDatabaseConnection(): Promise<boolean> {
  try {
    const client = await pool.connect();
    client.release();
    return true;
  } catch (error) {
    console.error('Database connection error:', error);
    return false;
  }
}

// Helper function to get a client from the pool with timeout
export async function getPoolClient(timeoutMs = 5000) {
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Connection timeout')), timeoutMs);
  });
  
  try {
    const clientPromise = pool.connect();
    const client = await Promise.race([clientPromise, timeoutPromise]);
    return client;
  } catch (error) {
    if (error.message === 'Connection timeout') {
      console.error('Database connection timeout');
    }
    throw error;
  }
}

// Graceful shutdown helper
export async function closePool() {
  try {
    await pool.end();
    console.log('Database pool has been closed');
  } catch (error) {
    console.error('Error closing database pool:', error);
    throw error;
  }
}
