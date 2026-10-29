# Discrete method

On Ω=(0,1)², use a uniform triangulation and the continuous P1 space Vh. The clean phantom has two smooth bright objects on a dark background. Add deterministic noise 0.14 sin(18πx)sin(22πy)+0.06 cos(26πx+14πy), then interpolate into Vh.

At each step m, compute cellwise P0 diffusivity g[m-1]=1/(1+|grad u[m-1]|²/kappa²). Find u[m] ∈ Vh such that, for every v ∈ Vh:

∫ u[m] v + dt ∫ g[m-1] grad u[m] · grad v = ∫ u[m-1] v.

The heat comparator sets g=1. Both use natural homogeneous Neumann flux conditions. The mass matrix plus a nonnegative weighted stiffness matrix gives an SPD discrete step, solved by UMFPACK. Taking v=1 gives exact discrete mass conservation up to roundoff. Constant initial fields remain constant. The heat equation's gradient seminorm decreases under backward Euler.

For a P1 solution, the gradient is constant on each element and discontinuous between elements. A P0 coefficient is a direct representation of its element gradient norm. The earlier P1 interpolation of this coefficient imposed a nodal convention on those discontinuities; the new cellwise choice is explicit.

The default mesh resolves the chosen noise frequencies. The coursework used sin(80πx) on nodes x=i/80, where that factor equals sin(iπ)=0. Its dominant noise component was therefore aliased away. Changing frequencies creates a meaningful resolved benchmark. Very coarse custom meshes can still alias the revised signal; do not compare resolutions without auditing sampling.

L² errors are integrated between finite-element fields (the clean reference is also P1-interpolated), not treated as pixel RMSE. The H¹ seminorm measures gradient smoothing; by itself it does not prove preservation of perceptually important edges. Exported nodal images use a shared [0,1] grayscale display; the numerical solver is not clipped to that interval.

The original Perona–Malik continuum equation can exhibit forward/backward diffusion and ill-posedness. Positive lagged conductivities give well-defined discrete linear steps, but this does not prove continuum well-posedness, unconditional consistency under refinement, or convergence to a unique continuum solution. There is no mesh/time convergence claim in this benchmark.

Both final-time errors and the best sampled errors of each method are reported. Best steps are chosen using the clean truth and must be labeled oracle. Hyperparameters are illustrative and assessed on this single phantom, so they do not demonstrate out-of-sample denoising performance.

Reference: Perona and Malik (1990), https://doi.org/10.1109/34.56205; FreeFEM documentation, https://doc.freefem.org/.
