"""Run the v7 Section 11 synthetic paper-results reproduction.

This repository generates synthetic toy covariance matrices only. It does not
use real CMB data, Planck maps, CLASS/CAMB, COMPACT eigenmodes, masks, beams,
foreground models, or a Planck likelihood. It is a proof-of-method companion
for reproducing the synthetic outputs described in the paper draft.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viscollapse.figures import (  # noqa: E402
    plot_covariance_blocks,
    plot_injected_recovered,
    plot_sn_scan,
)
from viscollapse.paper import (  # noqa: E402
    DEFAULT_FIGURES_DIR,
    DEFAULT_RESULTS_DIR,
    build_paper_reproduction,
    validate_paper_reproduction,
    write_paper_outputs,
)

DISCLAIMER = (
    "Synthetic paper-results reproduction only: no real CMB data, Planck maps, "
    "CLASS/CAMB, COMPACT eigenmodes, masks, beams, foregrounds, or likelihoods."
)


def main(argv: list[str] | None = None) -> int:
    """Run the full synthetic reproduction and return a process exit code."""
    args = _parse_args(argv)
    results_dir = _resolve_output_dir(args.output_dir)
    figures_dir = _resolve_output_dir(args.figures_dir)

    bundle = build_paper_reproduction()
    failures = validate_paper_reproduction(bundle)
    if failures:
        print("Synthetic paper-results validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    output_paths = write_paper_outputs(bundle, results_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    plot_covariance_blocks(figures_dir / "covariance_blocks.png")
    plot_sn_scan(bundle.scan, figures_dir / "sn_scan_lambda_fpaired.png")
    plot_injected_recovered(bundle.mc117, figures_dir / "injected_recovered.png")

    _print_summary(bundle, results_dir, figures_dir, output_paths)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reproduce the synthetic v7 Section 11 paper outputs.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_RESULTS_DIR),
        help="Directory for synthetic CSV/JSON outputs.",
    )
    parser.add_argument(
        "--figures-dir",
        default=str(DEFAULT_FIGURES_DIR),
        help="Directory for synthetic PNG outputs.",
    )
    return parser.parse_args(argv)


def _resolve_output_dir(path: str) -> Path:
    output = Path(path)
    if not output.is_absolute():
        output = ROOT / output
    return output


def _print_summary(bundle, results_dir: Path, figures_dir: Path, output_paths: dict[str, Path]) -> None:
    print("Synthetic paper-results reproduction complete.")
    print(DISCLAIMER)
    print(f"Results written to {results_dir}")
    print(f"Figures written to {figures_dir}")
    print(f"Manifest written to {output_paths['reproduction_manifest']}")

    projection = bundle.projection
    print("\nProjection check:")
    print(f"||P_vis tau_1 P_vis||_F = {projection['odd_projection_fro_norm']:.6g}")
    print(f"||P_vis I P_vis||_F     = {projection['even_projection_fro_norm']:.6g}")

    covariance = {
        row.template: row._asdict()
        for row in bundle.covariance_summary.itertuples(index=False)
    }
    print("\n6x6 summary:")
    _print_template_summary(covariance["6x6 toy block"])

    print("\n6x6 estimator recovery:")
    print(bundle.mc6[["A_inj", "Ahat_mean", "Ahat_SE", "status"]].to_string(index=False))

    print("\n117-mode summary:")
    one17 = covariance["117-mode synthetic ring"]
    print(f"N_modes              = {int(one17['n_modes'])}")
    _print_template_summary(one17)

    print("\n117-mode estimator recovery:")
    print(bundle.mc117[["A_inj", "Ahat_mean", "Ahat_SE", "status"]].to_string(index=False))

    print("\nLambda_b -- fpaired scan:")
    print(bundle.scan.round(4).to_string(index=False))


def _print_template_summary(summary: dict[str, float]) -> None:
    print(f"Tr(Delta C)         = {summary['trace']:.6g}")
    print(f"Tr(Delta C^2)       = {summary['trace_square']:.6g}")
    print(f"F_A                 = {summary['fisher']:.6g}")
    print(f"sigma_A             = {summary['sigma_A']:.6g}")


if __name__ == "__main__":
    raise SystemExit(main())
