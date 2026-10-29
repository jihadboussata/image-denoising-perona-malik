"""Run a headless FreeFEM benchmark and regenerate every figure."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def solve(output, n=80, steps=80, dt=.0005, kappa=1., constant=False, executable="FreeFem++"):
    if n < 4 or steps < 1 or dt <= 0 or kappa <= 0:
        raise ValueError("Require n >= 4, steps >= 1, dt > 0 and kappa > 0.")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    executable = shutil.which(executable)
    if executable is None:
        raise RuntimeError("FreeFem++ is required; see README installation instructions.")
    parameters = dict(n=n, steps=steps, dt=dt, kappa=kappa, constant=constant)
    config = f"int n={n}, steps={steps}; real dt={dt:.17g}, kappa={kappa:.17g}; bool constantCase={str(constant).lower()};\n"
    (output / "run.edp").write_text(config + (ROOT / "solver/denoise.edp").read_text())
    result = subprocess.run([executable, "-nw", "-v", "0", "run.edp"], cwd=output,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (output / "solver.log").write_text(result.stdout)
    if result.returncode:
        raise RuntimeError(f"FreeFEM failed; inspect {output / 'solver.log'}")
    (output / "parameters.json").write_text(json.dumps(parameters, indent=2) + "\n")
    return output


def figures(output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    output = Path(output)
    history = pd.read_csv(output / "history.csv")
    initial = pd.read_csv(output / "initial.csv")
    final = pd.read_csv(output / "final.csv")
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4))
    for ax, frame, column, title in zip(axes, [initial, initial, final, final],
        ["clean", "noisy", "perona_malik", "heat"], ["Clean reference", "Noisy input", "Perona–Malik", "Heat equation"]):
        image = frame.pivot(index="y", columns="x", values=column)
        ax.imshow(image, origin="lower", extent=(0,1,0,1), cmap="gray", vmin=0, vmax=1)
        ax.set_title(title); ax.set(xticks=[], yticks=[])
    fig.suptitle("P1 finite elements · same initial data and diffusion time", fontsize=12)
    fig.tight_layout(); fig.savefig(output / "comparison.png", dpi=180); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
    for method, label, color in [("pm", "Perona–Malik", "#007f86"), ("heat", "Heat", "#ce6c31")]:
        axes[0].plot(history.time, history[f"l2_{method}"], label=label, color=color)
        axes[1].plot(history.time, history[f"h1_{method}"], label=label, color=color)
    axes[0].set(xlabel="Diffusion time", ylabel="L² error to clean reference", title="Error trajectory")
    axes[1].set(xlabel="Diffusion time", ylabel="H¹ seminorm", title="Gradient smoothing")
    for ax in axes: ax.legend(); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(output / "diagnostics.png", dpi=160); plt.close(fig)
    summary = {"initial_l2": float(history.l2_pm.iloc[0]),
        "final_l2_pm": float(history.l2_pm.iloc[-1]), "final_l2_heat": float(history.l2_heat.iloc[-1]),
        "best_pm_step": int(history.loc[history.l2_pm.idxmin(), "step"]),
        "best_heat_step": int(history.loc[history.l2_heat.idxmin(), "step"]),
        "best_l2_pm": float(history.l2_pm.min()), "best_l2_heat": float(history.l2_heat.min()),
        "max_mass_drift_pm": float(np.max(np.abs(history.mass_pm - history.mass_pm.iloc[0]))),
        "max_mass_drift_heat": float(np.max(np.abs(history.mass_heat - history.mass_heat.iloc[0])))}
    (output / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--n", type=int, default=80)
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--dt", type=float, default=.0005)
    parser.add_argument("--kappa", type=float, default=1.)
    parser.add_argument("--freefem", default="FreeFem++")
    args = parser.parse_args()
    try:
        figures(solve(args.output, args.n, args.steps, args.dt, args.kappa, executable=args.freefem))
    except (RuntimeError, ValueError) as error:
        sys.exit(str(error))
