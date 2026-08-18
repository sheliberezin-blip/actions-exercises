const express = require('express');
const { Pool } = require('pg');
const Redis   = require('ioredis');

const app = express();
app.use(express.json());

// ─── Database connection ───────────────────────────────────────────
const pool = new Pool({
  host:     process.env.DB_HOST,
  user:     process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  port:     5432,
});

// ─── Redis connection ──────────────────────────────────────────────
const redis = new Redis({
  host: process.env.REDIS_HOST || 'cache',
  port: 6379,
});

const CACHE_KEY = 'items:all';
const CACHE_TTL = 30; // seconds

// ─── Retry connecting to PostgreSQL ───────────────────────────────
async function connectWithRetry(retries = 10, delayMs = 3000) {
  for (let i = 1; i <= retries; i++) {
    try {
      const client = await pool.connect();
      client.release();
      console.log('✅ Database connected');
      return;
    } catch (err) {
      console.log(`⏳ DB attempt ${i}/${retries}: ${err.message}`);
      if (i < retries) await new Promise(r => setTimeout(r, delayMs));
    }
  }
  throw new Error('Could not connect to PostgreSQL');
}

// ─── Routes ───────────────────────────────────────────────────────

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Node.js!', runtime: `Node.js ${process.version}` });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/items', async (req, res) => {
  try {
    const cached = await redis.get(CACHE_KEY);
    if (cached) {
      console.log('FROM CACHE ✅');
      return res.json(JSON.parse(cached));
    }
    console.log('FROM DB 🗄️');
    const { rows } = await pool.query('SELECT * FROM items ORDER BY created_at DESC');
    await redis.setex(CACHE_KEY, CACHE_TTL, JSON.stringify(rows));
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/items/:name', async (req, res) => {
  try {
    const { rows } = await pool.query(
      'INSERT INTO items (name) VALUES ($1) RETURNING *',
      [req.params.name]
    );
    await redis.del(CACHE_KEY);
    res.status(201).json(rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/items/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM items WHERE id = $1', [req.params.id]);
    if (result.rowCount === 0)
      return res.status(404).json({ error: 'Item not found' });
    await redis.del(CACHE_KEY);
    res.json({ deleted: true, id: Number(req.params.id) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/cache-stats', async (req, res) => {
  try {
    const keys = await redis.dbsize();
    res.json({ keys });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─── Start server ─────────────────────────────────────────────────
connectWithRetry().then(() => {
  app.listen(3000, '0.0.0.0', () => console.log('🚀 API listening on port 3000'));
});
