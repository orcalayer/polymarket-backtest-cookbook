# Polymarket Backtest Cookbook

Ready-to-run notebooks for backtesting **copy-trade strategies** on Polymarket
**smart-money** data, via the [OrcaLayer API](https://orcalayer.com/developers).

OrcaLayer reads every Polymarket trade from the chain (1.2B+ on-chain fills),
filters out farmers and hedgers, and corrects realized P&L (NegRisk halving,
per-wallet FIFO). These notebooks turn that into equity curves that answer one
question: *"what would copying this wallet — or this cohort — actually have
returned?"*

> ⚠️ **Informational only — NOT financial advice.** Past performance does not
> predict future results. This is a data-analysis demo built on historical,
> already-resolved markets; it is not a trading product or a recommendation.

## What's inside

| Notebook | What it does |
|---|---|
| [`01_follow_one_whale`](notebooks/01_follow_one_whale.ipynb) | Equity curve of copying every resolved bet of a single smart whale. |
| [`02_follow_smart_consensus`](notebooks/02_follow_smart_consensus.ipynb) | Blend a category's smart cohort into one cohort equity curve vs a flat baseline. |
| [`03_farmer_trap`](notebooks/03_farmer_trap.ipynb) | Raw "top traders" vs farmer-filtered top, side by side — the filter's value in real P&L. |

Each notebook is committed as both a reviewable `.py` (jupytext *percent*
format) and a runnable `.ipynb`.

## Quickstart

```bash
git clone https://github.com/orcalayer/polymarket-backtest-cookbook.git
cd polymarket-backtest-cookbook
pip install -r requirements.txt
cp .env.example .env          # then put your Premium key in ORCALAYER_API_KEY
jupyter lab                   # open the notebooks/ folder
```

- The **leaderboard** (wallet discovery) is **keyless**.
- The per-wallet **`/backtest`** endpoint is **Premium** — get a key at
  [orcalayer.com/pricing](https://orcalayer.com/pricing) and set it as
  `ORCALAYER_API_KEY` in your `.env`.

### Open in Colab

Each notebook can be opened directly in Google Colab (add your key via
`os.environ["ORCALAYER_API_KEY"]` in the first cell):

`https://colab.research.google.com/github/orcalayer/polymarket-backtest-cookbook/blob/main/notebooks/01_follow_one_whale.ipynb`

## Data sources

| Call | Auth | Via |
|---|---|---|
| `leaderboard(sort, category, filter, limit)` | keyless | `orcalayer` SDK |
| `GET /api/v2/whale/{address}/backtest?limit=` | **Premium** | thin `httpx` wrapper (no SDK method yet) |

`/backtest` returns resolved positions per outcome — `market_id`, `side`,
`avg_entry_price`, `pnl`, `won`, `category`, `resolved_at` — plus a `summary`
(`total`, `resolved`, `wins`, `losses`, `win_rate`, `total_pnl`). The `pnl`
already encodes OrcaLayer's NegRisk/FIFO/farmer methodology, so the notebooks
never reconcile it against any other source — that *is* the point.

## Links

- **Developers:** https://orcalayer.com/developers
- **Get a key / pricing:** https://orcalayer.com/pricing
- **Methodology** (smart money, the farmer filter): https://orcalayer.com/methodology

## License

MIT — see [LICENSE](LICENSE).
