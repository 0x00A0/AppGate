from appgate import Runway, Approach
from ui import launch_ui

if __name__ == "__main__":
    ZBAA_01 = Runway(elev=25.5, rdh=15.0)
    ils = Approach(theta=3.0, d=2.0)

    launch_ui(ZBAA_01, ils, plot_max_km=25.0)
