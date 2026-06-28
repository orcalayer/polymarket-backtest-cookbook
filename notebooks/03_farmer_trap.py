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
# # 03 · The Farmer Trap
#
# A naive "copy the top traders by P&L" leaderboard is full of **farmers** —
# wallets that buy near-decided markets at ~99¢ to manufacture flawless win
# rates. OrcaLayer's `filter=smart` excludes them. This notebook copies **both**
# cohorts and plots their equity curves side by side, so the farmer filter's
# value shows up in real P&L instead of a footnote.
#
# Same leaderboard, two filters — apples to apples:
# `filter="all"` (raw, farmers included) vs `filter="smart"` (farmers excluded).
#
# **API tiers:** the leaderboard calls below are **keyless**; only the per-wallet
# `/backtest` (run inside `blend_cohort`) needs your Premium `ORCALAYER_API_KEY`.
# Do **not** pass a key to the leaderboard — that triggers a 403.
#
# > ⚠️ **Informational only — NOT financial advice.** Past performance does not
# > predict future results.

# %% [markdown]
# > **Running in Google Colab?** Uncomment and run the next cell first — it
# > installs dependencies, pulls the repo for the shared `utils/` helper, and
# > prompts for your key. Skip it if you cloned the repo and run locally.

# %%
# --- Colab setup: in Colab, remove the leading "# " from each line and run ---
# !pip install -q orcalayer==0.1.3 pandas matplotlib httpx python-dotenv
# !git clone -q https://github.com/orcalayer/polymarket-backtest-cookbook.git
# %cd polymarket-backtest-cookbook/notebooks
# import os, getpass
# os.environ["ORCALAYER_API_KEY"] = getpass.getpass("OrcaLayer Premium API key: ")

# %%
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# %matplotlib inline
import matplotlib.pyplot as plt
import pandas as pd

from utils.oc_backtest import leaderboard, blend_cohort

# %%
N = 8

raw_cohort = leaderboard(filter="all", limit=N)     # raw top P&L — includes farmers
smart_cohort = leaderboard(filter="smart", limit=N)  # farmer/hedger-filtered

print("RAW top (filter=all):")
for w in raw_cohort:
    print(f"  {w.get('name') or w['wallet'][:12]:20s}  ${w.get('total_pnl', 0):>14,.0f}  WR {w.get('win_rate')}%")
print("\nSMART top (filter=smart):")
for w in smart_cohort:
    print(f"  {w.get('name') or w['wallet'][:12]:20s}  ${w.get('total_pnl', 0):>14,.0f}  WR {w.get('win_rate')}%")

# %% [markdown]
# Backtest and blend each cohort into its own equity curve.

# %%
raw_curve, raw_sum = blend_cohort(raw_cohort, limit=500)
smart_curve, smart_sum = blend_cohort(smart_cohort, limit=500)
raw_curve["date"] = pd.to_datetime(raw_curve["last_trade_ts"], unit="s")
smart_curve["date"] = pd.to_datetime(smart_curve["last_trade_ts"], unit="s")

# %%
plt.figure(figsize=(11, 5.5))
plt.plot(raw_curve["date"], raw_curve["equity"], lw=2, color="#d62728",
         label=f'Raw "top traders" (filter=all, n={len(raw_cohort)})')
plt.plot(smart_curve["date"], smart_curve["equity"], lw=2, color="#1f77b4",
         label=f"Farmer-filtered top (filter=smart, n={len(smart_cohort)})")
plt.axhline(0, color="grey", lw=1, ls="--")
plt.title("The Farmer Trap — copying raw top traders vs the farmer-filtered top")
plt.xlabel("resolution date")
plt.ylabel("cumulative P&L ($)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %% [markdown]
# Side-by-side final numbers.

# %%
raw_final = float(raw_curve["equity"].iloc[-1]) if not raw_curve.empty else 0.0
smart_final = float(smart_curve["equity"].iloc[-1]) if not smart_curve.empty else 0.0
print(f'Raw "top traders"   final P&L: ${raw_final:,.0f}')
print(f"Farmer-filtered top final P&L: ${smart_final:,.0f}")

# %% [markdown]
# A raw P&L leaderboard rewards the farmer's manufactured 99% win rate — but
# that "edge" doesn't transfer to a copy-trader, because the farmer was buying
# near-certain outcomes for pennies of profit at huge size and tail risk. The
# `filter=smart` cohort excludes that pattern up front.
#
# This is exactly why a 99% win rate is a trap, not a signal. See:
# - Methodology: https://orcalayer.com/methodology
# - "Why a 99% win rate is a trap": https://orcalayer.com/blog
#
# > ⚠️ Informational only — not financial advice.
