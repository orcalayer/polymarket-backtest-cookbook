# Polymarket Backtest Cookbook

Ready-to-run notebooks to backtest copy-trade ideas on Polymarket smart-money
data via the [OrcaLayer API](https://orcalayer.com/developers).

## Who it's for

Developers building Polymarket bots, or anyone testing a "copy this wallet" idea
on historical, already-resolved markets **before risking real money**.

> **Informational and educational only. This is not financial advice. Backtests
> use historical resolved markets; past performance does not predict future
> results.**

## Quickstart

Tested on **Python 3.12**.

```bash
git clone https://github.com/orcalayer/polymarket-backtest-cookbook.git
cd polymarket-backtest-cookbook

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # then add your Premium key to ORCALAYER_API_KEY

jupyter lab                      # open the notebooks/ folder
```

> **The key, and the 403 trap.** The public **leaderboard works WITHOUT a key**.
> The per-wallet **`/backtest` REQUIRES a Premium key**. Sending a key *to the
> leaderboard* returns **403** — so the notebooks only attach the key to
> `/backtest`. Get a key at [orcalayer.com/pricing](https://orcalayer.com/pricing).

## The notebooks

**`01_follow_one_whale`** — what would copying every resolved bet of a single
smart-money wallet have returned? Pulls the wallet's resolved positions, builds a
cumulative-P&L equity curve, and reports final P&L, win rate, max drawdown and
resolved-market count.

**`02_follow_smart_consensus`** — instead of one wallet, copy a whole smart-money
cohort for a category. Pulls the top smart wallets (keyless leaderboard),
backtests each, and blends them into one equal-weight cohort equity curve versus
a flat baseline.

**`03_farmer_trap`** — copying the raw top-P&L traders (farmers included) versus
the farmer-filtered top, side by side on one chart. The **gap between the two
curves is the point**: a naive "top traders" leaderboard rewards farmers who buy
near-decided markets at ~99¢ to manufacture flawless win rates; OrcaLayer's
`filter=smart` excludes them. Run it to see the current numbers.

## Results vary

Every number comes from **live data** and will differ each run as new markets
resolve. The notebooks intentionally hardcode no results — run them to see
current figures.

## Rate limits

The API allows **300 requests/min**. The cohort notebooks (02, 03) loop over many
wallets calling `/backtest`, so they are throttled with a short sleep between
calls to stay under the limit on a fresh run.

## Links

- Developers: https://orcalayer.com/developers
- API docs: https://orcalayer.com/docs
- Methodology (smart money, the farmer filter): https://orcalayer.com/methodology
- Pricing / get a key: https://orcalayer.com/pricing

## License

MIT — see [LICENSE](LICENSE).
