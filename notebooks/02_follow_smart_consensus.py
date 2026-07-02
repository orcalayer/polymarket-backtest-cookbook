# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 02 · Follow the Smart Consensus
#
# Instead of one wallet, copy a whole **smart-money cohort** for a category. We
# take the top smart wallets from the keyless leaderboard, backtest each, and
# blend them into one equal-weight cohort equity curve — then compare it to a
# flat (do-nothing) baseline.
#
# **API tiers:** the leaderboard is **keyless**; only the per-wallet `/backtest`
# (run inside `blend_cohort`) needs your Premium `ORCALAYER_API_KEY`. Do **not**
# pass a key to the leaderboard — it wastes a round-trip (the SDK v0.2+ falls back to public).
#
# > ⚠️ **Informational only — NOT financial advice.** Past performance does not
# > predict future results.

# %% [markdown]
# > **Running in Google Colab?** Paste the snippet below into a new cell and run
# > it first (installs dependencies, pulls the repo for the shared `utils/`
# > helper, and prompts for your key), then continue from the next cell. Skip
# > this if you cloned the repo and run locally.
# >
# > ```python
# > !pip install -q orcalayer==0.2.0 pandas matplotlib httpx python-dotenv
# > !git clone https://github.com/orcalayer/polymarket-backtest-cookbook.git
# > %cd polymarket-backtest-cookbook/notebooks
# > import os, getpass
# > os.environ["ORCALAYER_API_KEY"] = getpass.getpass("OrcaLayer Premium API key: ")
# > ```

# %%
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# %matplotlib inline
import matplotlib.pyplot as plt
import pandas as pd

from utils.oc_backtest import leaderboard, blend_cohort

# %% [markdown]
# Choose a category and cohort size. The leaderboard call is keyless;
# `filter="smart"` applies OrcaLayer's farmer/hedger exclusion.

# %%
CATEGORY = "Crypto"
N = 8

cohort = leaderboard(category=CATEGORY, filter="smart", limit=N)
print(f"{len(cohort)} smart wallets in {CATEGORY}:")
for w in cohort:
    print(f"  {w.get('name') or w['wallet'][:12]:20s}  ${w.get('total_pnl', 0):>14,.0f}  WR {w.get('win_rate')}%")

# %% [markdown]
# Backtest every wallet and blend them. `blend_cohort` sums P&L by resolution
# time across the cohort (an equal-weight "copy them all" portfolio) and paces
# the loop under the 600-requests/min rate limit.

# %%
curve, summaries = blend_cohort(cohort, limit=500)
curve["date"] = pd.to_datetime(curve["last_trade_ts"], unit="s")
pd.DataFrame(summaries)[["name", "wallet", "resolved", "win_rate", "total_pnl"]]

# %%
plt.figure(figsize=(11, 5))
plt.plot(curve["date"], curve["equity"], lw=2, color="#2ca02c",
         label=f"{CATEGORY} smart cohort (n={len(cohort)})")
plt.axhline(0, color="grey", lw=1.2, ls="--", label="flat baseline (no strategy)")
plt.title(f"Copying the {CATEGORY} smart-money consensus — blended cumulative P&L")
plt.xlabel("resolution date")
plt.ylabel("cumulative P&L ($)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %% [markdown]
# Headline numbers for the blended cohort.

# %%
final_pnl = float(curve["equity"].iloc[-1]) if not curve.empty else 0.0
print(f"Cohort final P&L:   ${final_pnl:,.0f}")
print(f"Resolved positions: {len(curve)}")
print(f"Wallets blended:    {len(cohort)}")

# %% [markdown]
# Blending several smart wallets smooths out any single wallet's luck — it
# approximates "follow the consensus" rather than betting on one trader. It is
# still a backward-looking measurement on resolved markets, **not** a forward
# prediction.
#
# > ⚠️ Informational only — not financial advice.
