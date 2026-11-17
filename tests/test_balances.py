"""Tests for the v0 model: physical balances and economic behaviour."""
import pytest

from utilities_optimizer.model import DEFAULT_PARAMS, solve

TOL = 1e-6


@pytest.fixture
def r():
    return solve(DEFAULT_PARAMS)


# --- Physics: mass and energy are conserved ---------------------------------

def test_hp_balance(r):
    p = DEFAULT_PARAMS
    produced = r["B1"] + r["B2"]
    consumed = p["demand_hp_t_h"] + r["F_cp"] + r["F_v"] + r["F_cd"]
    assert produced == pytest.approx(consumed, abs=TOL)


def test_lp_balance(r):
    assert r["F_cp"] + r["F_v"] == pytest.approx(
        DEFAULT_PARAMS["demand_lp_t_h"], abs=TOL
    )


def test_el_balance(r):
    p = DEFAULT_PARAMS
    supplied = p["e_cp_mwh_t"] * r["F_cp"] + p["e_cd_mwh_t"] * r["F_cd"] + r["P_buy"]
    assert supplied == pytest.approx(p["demand_el_mw"], abs=TOL)


def test_capacities_respected(r):
    p = DEFAULT_PARAMS
    assert r["B1"] <= p["cap_b1_t_h"] + TOL
    assert r["B2"] <= p["cap_b2_t_h"] + TOL
    assert r["F_cp"] <= p["cap_cp_t_h"] + TOL
    assert r["F_cd"] <= p["cap_cd_t_h"] + TOL


# --- Economics: reference case and break-even price -------------------------

def test_reference_cost(r):
    # 25*50 + 30*10 + 90*2.8 = 1802 EUR/h
    assert r["cost_eur_h"] == pytest.approx(1802, abs=TOL)


def test_letdown_valve_closed(r):
    # LP steam through the back-pressure turbine yields free power: valve unused
    assert r["F_v"] == pytest.approx(0, abs=TOL)


def test_condensing_off_below_breakeven():
    p = {**DEFAULT_PARAMS, "price_el_eur_mwh": 140}
    assert solve(p)["F_cd"] == pytest.approx(0, abs=TOL)


def test_condensing_on_above_breakeven():
    # Break-even = c2 / e_cd = 30 / 0.2 = 150 EUR/MWh
    # Above it, F_cd covers the remaining 2.8 MW: 2.8 / 0.2 = 14 t/h, P_buy = 0
    p = {**DEFAULT_PARAMS, "price_el_eur_mwh": 160}
    res = solve(p)
    assert res["F_cd"] == pytest.approx(14, abs=TOL)
    assert res["P_buy"] == pytest.approx(0, abs=TOL)