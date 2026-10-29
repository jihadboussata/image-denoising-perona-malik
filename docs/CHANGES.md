# Portfolio revision

- Replaced assignment presentation and Windows-specific folder commands with a headless, parameterized, cross-platform Python runner.
- Corrected the noise/mesh aliasing that suppressed the original 80π oscillation at mesh nodes.
- Represented lagged diffusivity in P0, consistent with cellwise P1 gradients.
- Exported full error histories, nodal fields, parameters and matched-comparison figures.
- Reported oracle-best stopping times for both methods alongside final-time results, with clear interpretation limits.
- Added constant-field, mass-conservation and heat-smoothing checks; ran the actual FreeFEM solver.
- Documented discrete solvability separately from the continuum Perona–Malik well-posedness problem.
