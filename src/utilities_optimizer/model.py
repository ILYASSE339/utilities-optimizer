"""Utilities optimizer — v0: minimal steady-state steam and power model."""
import pyomo.environ as pyo

DEFAULT_PARAMS = {
    "demand_hp_t_h": 20,
    "demand_lp_t_h": 40,
    "demand_el_mw": 6,
    "cost_b1_eur_t": 25, "cap_b1_t_h": 50,
    "cost_b2_eur_t": 30, "cap_b2_t_h": 40,
    "e_cp_mwh_t": 0.08, "cap_cp_t_h": 40,
    "e_cd_mwh_t": 0.20, "cap_cd_t_h": 30,
    "price_el_eur_mwh": 90,
}


def build_model(p: dict) -> pyo.ConcreteModel:
    m = pyo.ConcreteModel()

    # Variables de décision (t/h et MW), toutes positives
    m.B1 = pyo.Var(bounds=(0, p["cap_b1_t_h"]))
    m.B2 = pyo.Var(bounds=(0, p["cap_b2_t_h"]))
    m.F_cp = pyo.Var(bounds=(0, p["cap_cp_t_h"]))
    m.F_v = pyo.Var(bounds=(0, None))
    m.F_cd = pyo.Var(bounds=(0, None))
    m.P_buy = pyo.Var(bounds=(0, None))

    # Bilans
    m.balance_hp = pyo.Constraint(expr = m.B1 + m.B2 == m.F_cp + m.F_v + m.F_cd + p["demand_hp_t_h"])
    m.balance_lp = pyo.Constraint(expr = m.F_v + m.F_cp == p["demand_lp_t_h"])
    m.balance_el = pyo.Constraint(expr= p["e_cp_mwh_t"] * m.F_cp + p["e_cd_mwh_t"] * m.F_cd + m.P_buy == p["demand_el_mw"])

    # Objectif : coût horaire (€/h)
    m.cost = pyo.Objective(expr = p["cost_b1_eur_t"] * m.B1 + p["cost_b2_eur_t"] * m.B2 + p["price_el_eur_mwh"] * m.P_buy, sense=pyo.minimize)
    return m


def solve(p: dict = DEFAULT_PARAMS) -> dict:
    m = build_model(p)
    pyo.SolverFactory("appsi_highs").solve(m)
    result = {v.name: pyo.value(v) for v in m.component_objects(pyo.Var)}
    result["cost_eur_h"] = pyo.value(m.cost)
    return result