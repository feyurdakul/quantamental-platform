/**
 * TradingView Gateway REST Bridge Server (@mathieuc/tradingview)
 * Python Backend için milisaniyelik canlı mum ve Pine Script API uç noktaları sağlar.
 */

const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Sağlık kontrolü
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'TradingView Gateway',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Tarihsel ve Canlı OHLCV endpoint'i
app.get('/ohlcv/:symbol', async (req, res) => {
  const { symbol } = req.params;
  const tf = req.query.tf || '1D';
  const barsCount = parseInt(req.query.bars, 10) || 250;

  try {
    const TradingView = require('@mathieuc/tradingview');
    const client = new TradingView.Client();
    const chart = new client.Session.Chart();

    chart.setMarket(symbol, {
      timeframe: tf,
      range: barsCount
    });

    // Mumlar hazır olduğunda dön
    const timeout = setTimeout(() => {
      chart.delete();
      client.end();
      return res.status(504).json({ error: 'TradingView socket timeout' });
    }, 5000);

    chart.onUpdate(() => {
      if (chart.periods && chart.periods.length > 0) {
        clearTimeout(timeout);
        const bars = chart.periods.map(p => ({
          time: p.time,
          open: p.open,
          high: p.max,
          low: p.min,
          close: p.close,
          volume: p.volume
        }));

        chart.delete();
        client.end();

        return res.json({
          symbol,
          timeframe: tf,
          count: bars.length,
          bars
        });
      }
    });

    chart.onError((err) => {
      clearTimeout(timeout);
      chart.delete();
      client.end();
      return res.status(500).json({ error: String(err) });
    });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
});

// TradingView TA Konsensüsü (Strong Buy / Buy / Neutral / Sell / Strong Sell)
app.get('/ta/:symbol', async (req, res) => {
  const { symbol } = req.params;
  try {
    const TradingView = require('@mathieuc/tradingview');
    const ta = await TradingView.getTA(symbol);
    return res.json({
      symbol,
      summary: ta.summary,
      oscillators: ta.oscillators,
      movingAverages: ta.moving_averages
    });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 TradingView Gateway running on port ${PORT}`);
});
