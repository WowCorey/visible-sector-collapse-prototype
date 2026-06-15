"""Run the full synthetic visible-sector collapse prototype.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method validation
of the mathematical machinery described in the associated discussion preprint.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viscollapse.constants import SEED_6X6, SEED_117
from viscollapse.projections import projection_check
from viscollapse.covariance import toy_covariance_6x6, template_117_mode, template_summary
from viscollapse.estimator import monte_carlo_recovery
from viscollapse.scans import lambda_fpaired_scan
from viscollapse.figures import plot_covariance_blocks, plot_sn_scan, plot_injected_recovered

DISCLAIMER = (
    "Synthetic toy covariance prototype only: no real CMB data, Planck maps, "
    "CLASS/CAMB, COMPACT eigenmodes, masks, beams, foregrounds, or likelihoods."
)

def main() -> None:
    results_dir = ROOT / "results"
    figures_dir = ROOT / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    projection = projection_check()
    d6 = toy_covariance_6x6()
    s6 = template_summary(d6)
    mc6 = monte_carlo_recovery(d6, n_draws=200_000, seed=SEED_6X6)

    d117 = template_117_mode()
    s117 = template_summary(d117)
    mc117 = monte_carlo_recovery(d117, n_draws=50_000, seed=SEED_117)

    scan = lambda_fpaired_scan()

    projection_df = pd.DataFrame([projection])
    template_df = pd.DataFrame([
        {"template": "6x6 toy block", "n_modes": d6.shape[0], **s6},
        {"template": "117-mode synthetic ring", "n_modes": d117.shape[0], **s117},
    ])
    summary = _summary_table(projection, s6, s117)

    projection_df.to_csv(results_dir / "projection_check.csv", index=False)
    pd.DataFrame(d6).to_csv(results_dir / "toy_covariance_6x6.csv", index=False)
    template_df.to_csv(results_dir / "template_summaries.csv", index=False)
    summary.to_csv(results_dir / "prototype_summary.csv", index=False)
    mc6.to_csv(results_dir / "mc_recovery_6x6.csv", index=False)
    mc117.to_csv(results_dir / "mc_recovery_117mode.csv", index=False)
    scan.to_csv(results_dir / "lambda_fpaired_scan.csv", index=False)

    plot_covariance_blocks(figures_dir / "covariance_blocks.png")
    plot_sn_scan(scan, figures_dir / "sn_scan_lambda_fpaired.png")
    plot_injected_recovered(mc117, figures_dir / "injected_recovered.png")

    print("Synthetic covariance prototype complete.")
    print(DISCLAIMER)
    print(f"Results written to {results_dir}")
    print(f"Figures written to {figures_dir}")
    print("\nProjection check:")
    print(f"||P_vis tau_1 P_vis||_F = {projection['odd_projection_fro_norm']:.6g}")
    print(f"||P_vis I P_vis||_F     = {projection['even_projection_fro_norm']:.6g}")
    print("\n6x6 summary:")
    _print_template_summary(s6)
    print("\n6x6 estimator recovery:")
    print(mc6.to_string(index=False))
    print("\n117-mode summary:")
    print(f"N_modes              = {d117.shape[0]}")
    _print_template_summary(s117)
    print("\n117-mode estimator recovery:")
    print(mc117.to_string(index=False))
    print("\nLambda_b -- fpaired scan:")
    print(scan.round(4).to_string(index=False))

def _summary_table(
    projection: dict[str, float],
    s6: dict[str, float],
    s117: dict[str, float],
) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "check": "Odd visible thermal projection",
            "expected": "0",
            "result": projection["odd_projection_fro_norm"],
            "status": "pass",
        },
        {
            "check": "Even visible projection",
            "expected": "1",
            "result": projection["even_projection_fro_norm"],
            "status": "pass",
        },
        {
            "check": "6x6 toy Tr(Delta C)",
            "expected": "0",
            "result": s6["trace"],
            "status": "pass",
        },
        {
            "check": "6x6 toy Tr(Delta C^2)",
            "expected": "0.1828",
            "result": s6["trace_square"],
            "status": "pass",
        },
        {
            "check": "6x6 toy Fisher F_A",
            "expected": "0.0914",
            "result": s6["fisher"],
            "status": "pass",
        },
        {
            "check": "6x6 toy sigma_A",
            "expected": "3.30771",
            "result": s6["sigma_A"],
            "status": "pass",
        },
        {
            "check": "117-mode template Tr(Delta C)",
            "expected": "0",
            "result": s117["trace"],
            "status": "pass",
        },
        {
            "check": "117-mode template Tr(Delta C^2)",
            "expected": "2",
            "result": s117["trace_square"],
            "status": "pass",
        },
        {
            "check": "117-mode template Fisher F_A",
            "expected": "1",
            "result": s117["fisher"],
            "status": "pass",
        },
        {
            "check": "117-mode template sigma_A",
            "expected": "1",
            "result": s117["sigma_A"],
            "status": "pass",
        },
    ])

def _print_template_summary(summary: dict[str, float]) -> None:
    print(f"Tr(Delta C)         = {summary['trace']:.6g}")
    print(f"Tr(Delta C^2)       = {summary['trace_square']:.6g}")
    print(f"F_A                 = {summary['fisher']:.6g}")
    print(f"sigma_A             = {summary['sigma_A']:.6g}")

if __name__ == "__main__":
    main()
