"""oc_backtest.py — shared helpers for the OrcaLayer Backtest Cookbook.

Design:
- The smart-money **leaderboard** is fetched through the official ``orcalayer``
  SDK (the supported, versioned client). It is keyless.
- The **/backtest** endpoint has no SDK method yet, so it is fetched via a thin
  ``httpx`` wrapper against the same public API base. It is Premium (needs a key).

Nothing here is financial advice. See each notebook's disclaimer.
"""
from __future__ import annotations

import os
import time

import httpx
import pandas as pd
from dotenv import find_dotenv, load_dotenv

# Search upward from the current working directory so the key loads whether the
# notebook runs from the repo root or from inside notebooks/.
load_dotenv(find_dotenv(usecwd=True))

# The SDK and the raw /backtest call both target the public API base. External
# developers run against the default; nothing here is environment-specific.
API_BASE = os.getenv("ORCALAYER_API_BASE", "https://orcalayer.com")


def load_key() -> str | None:
    """Premium API key from the ORCALAYER_API_KEY env var (needed for /backtest)."""
    return os.getenv("ORCALAYER_API_KEY") or None


def get_client(api_key: str | None = None):
    """Official OrcaLayer SDK client.

    Defaults to anonymous: the leaderboard is keyless, and passing a key there
    triggers Premium-subscription validation we don't need for discovery.
    """
    from orcalayer import OrcaLayer

    return OrcaLayer(api_key=api_key, base_url=API_BASE)


def leaderboard(sort: str = "pnl", category: str | None = None,
                filter: str = "smart", limit: int = 20) -> list[dict]:
    """Smart-money leaderboard via the SDK (keyless).

    ``filter="smart"`` = OrcaLayer's farmer/hedger-filtered cohort;
    ``filter="all"``   = raw top P&L, farmers included (used by notebook 3).
    Returns a list of wallet dicts (wallet, name, total_pnl, win_rate, ...).
    """
    client = get_client()
    try:
        data = client.leaderboard(sort=sort, category=category, filter=filter, limit=limit)
    finally:
        client.close()
    # SDK returns {"whales": [...], "total": N, ...}; be tolerant of a bare list.
    return data.get("whales", []) if isinstance(data, dict) else list(data)


def backtest(address: str, limit: int = 500, api_key: str | None = None) -> dict:
    """Resolved positions for one wallet via /whale/{addr}/backtest (PREMIUM).

    No SDK method exists for this yet, so it is a thin REST call. P&L already
    encodes OrcaLayer's NegRisk/FIFO/farmer methodology — do not reconcile it
    against any other source. Returns {"positions": [...], "summary": {...}}.
    """
    key = api_key or load_key()
    if not key:
        raise RuntimeError(
            "backtest is a Premium endpoint — set ORCALAYER_API_KEY in your .env. "
            "Get a key at https://orcalayer.com/pricing"
        )
    url = f"{API_BASE}/api/v2/whale/{address.lower()}/backtest"
    resp = httpx.get(url, params={"limit": limit},
                     headers={"X-API-Key": key}, timeout=30.0)
    resp.raise_for_status()
    return resp.json()


def positions_df(bt) -> pd.DataFrame:
    """Backtest payload -> tidy DataFrame of RESOLVED positions, time-sorted.

    Keeps only outcomes where ``won`` is True/False (drops PENDING/None), and
    orders by ``last_trade_ts`` (epoch) — the reliable time key for an equity
    curve (``resolved_at`` is a display string and can be sparse).
    """
    rows = bt.get("positions", []) if isinstance(bt, dict) else bt
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df[df["won"].notna()].copy()
    df["won"] = df["won"].astype(bool)
    df = df.sort_values("last_trade_ts").reset_index(drop=True)
    return df


def equity_curve(positions) -> pd.DataFrame:
    """Cumulative-P&L curve from resolved positions (DataFrame or raw list)."""
    df = positions if isinstance(positions, pd.DataFrame) else positions_df({"positions": positions})
    if df.empty:
        return pd.DataFrame(columns=["last_trade_ts", "pnl", "equity"])
    out = df[["last_trade_ts", "pnl"]].copy()
    out["equity"] = out["pnl"].cumsum()
    return out


def max_drawdown(curve) -> float:
    """Largest peak-to-trough drop of an equity curve. Returns <= 0."""
    eq = curve["equity"] if isinstance(curve, pd.DataFrame) else pd.Series(curve)
    if eq.empty:
        return 0.0
    drawdown = eq - eq.cummax()
    return round(float(drawdown.min()), 2)


def win_rate(positions) -> float:
    """Resolved-market win rate (%) from positions (DataFrame or raw list)."""
    df = positions if isinstance(positions, pd.DataFrame) else positions_df({"positions": positions})
    if df.empty:
        return 0.0
    return round(100.0 * df["won"].sum() / len(df), 1)


def blend_cohort(wallets, limit: int = 500, api_key: str | None = None,
                 sleep: float = 0.25):
    """Backtest several wallets and blend them into ONE cohort equity curve.

    Models an equal-weight "copy the whole cohort" portfolio: P&L is summed by
    resolution time across every wallet. ``wallets`` may be addresses or
    leaderboard dicts. ``sleep`` paces the loop under the 300/min rate limit.
    Returns ``(cohort_curve_df, per_wallet_summaries)``.
    """
    frames, summaries = [], []
    for w in wallets:
        addr = w if isinstance(w, str) else (w.get("wallet") or w.get("address"))
        if not addr:
            continue
        bt = backtest(addr, limit=limit, api_key=api_key)
        summaries.append({"wallet": addr, "name": (w.get("name") if isinstance(w, dict) else None),
                          **bt.get("summary", {})})
        df = positions_df(bt)
        if not df.empty:
            frames.append(df[["last_trade_ts", "pnl"]])
        time.sleep(sleep)
    if not frames:
        return pd.DataFrame(columns=["last_trade_ts", "pnl", "equity"]), summaries
    allpos = pd.concat(frames).sort_values("last_trade_ts")
    cohort = allpos.groupby("last_trade_ts", as_index=False)["pnl"].sum()
    cohort["equity"] = cohort["pnl"].cumsum()
    return cohort, summaries
