import matplotlib.pyplot as plt
import numpy as np

# Create a custom colormap for the difference
from matplotlib.colors import LinearSegmentedColormap

colors = [(1, 0.6, 0), (1, 1, 1), (0, 1, 0)]  # Orange -> White -> Green
custom_cmap = LinearSegmentedColormap.from_list("CustomMap", colors)


# Define the parameter space for LE and FV
LE = np.arange(101)
FV = np.arange(400)


# Define the EV and SV functions
def ev_less_p(
    le: float, fv: float, k: float = 0.05, sv: float = 0.01, a: float = 0.08
) -> float:
    return (fv - sv) / (1 + k * le) - a * fv


# def sv(le: float, fv: float, j: float = 0.05, le_0=3) -> float:
#     foo = 1 + j * np.abs(le_0 - le)
#     return fv * np.log(foo) / foo


# def sv(le: float, fv: float, j: float = 0.05, le_0=100) -> float:

#     return j * fv * (le_0 - le) * le


# plot sv against le

plt.figure(figsize=(10, 8))

# plt.plot(LE, [sv(le, 100) for le in LE], label="FV=100")

# Compute EV and SV arrays
EV = np.array([[ev_less_p(le, f) for le in LE] for f in FV])
# SV = np.array([[sv(le, f) for le in LE] for f in FV])

# Prepare grids for contour plots
LE_grid, FV_grid = np.meshgrid(LE, FV)

# Plot the EV heatmap
plt.figure(figsize=(10, 8))
plt.imshow(
    EV,
    aspect="auto",
    origin="lower",
    cmap=custom_cmap,
    extent=[LE.min(), LE.max(), FV.min(), FV.max()],
)
plt.colorbar(label="e-p")
plt.xlabel("LE")
plt.ylabel("FV")
plt.title("Heatmap of EV as a Function of LE and FV")

# Add an isoline for EV = 20, 40,  60 and have text notation
contour = plt.contour(
    LE_grid, FV_grid, EV, levels=[20, 40, 60], colors="red", linewidths=2
)
plt.clabel(contour, fmt="c=%d", inline=True, fontsize=10)


# contour = plt.contour(LE_grid, FV_grid, EV, levels=[40], colors="red", linewidths=2)
# plt.clabel(contour, fmt="c=40", inline=True, fontsize=10)
plt.show()

# # Plot the SV heatmap
# plt.figure(figsize=(10, 8))
# plt.imshow(
#     SV,
#     aspect="auto",
#     origin="lower",
#     cmap=custom_cmap,
#     extent=[LE.min(), LE.max(), FV.min(), FV.max()],
# )
# plt.colorbar(label="SV")
# plt.xlabel("LE")
# plt.ylabel("FV")
# plt.title("Heatmap of SV as a Function of LE and FV")
# plt.show()

# # Compute EV - SV and plot with custom colour map
# diff = EV - SV


# plt.figure(figsize=(10, 8))
# plt.imshow(
#     diff,
#     aspect="auto",
#     origin="lower",
#     cmap=custom_cmap,
#     extent=[LE.min(), LE.max(), FV.min(), FV.max()],
# )
# plt.colorbar(label="EV - SV")

# # Add an isoline for EV - SV = 20
# contour = plt.contour(LE_grid, FV_grid, diff, levels=[20], colors="blue", linewidths=2)
# plt.clabel(contour, fmt="c=20", inline=True, fontsize=10)

# plt.xlabel("LE")
# plt.ylabel("FV")
# plt.title("Heatmap of EV - SV as a Function of LE and FV")
# plt.show()
