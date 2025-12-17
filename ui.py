import dearpygui.dearpygui as dpg
from appgate import Runway, Approach


def launch_ui(initial_runway: Runway, initial_app: Approach, plot_max_km: float = 25.0):
    TAG = {
        "rw_elev": "rw_elev",
        "rw_rdh": "rw_rdh",
        "theta": "theta",
        "d": "d",
        "in_h": "in_h",
        "in_dist": "in_dist",
        "out_gate_dist": "out_gate_dist",
        "out_glide_alt": "out_glide_alt",
        "plot_max_km": "plot_max_km",
        "plot": "plot",
        "line": "ils_line",
        "sel_point": "sel_point",
        "x_axis": "x_axis",
        "y_axis": "y_axis",
        "gate_box": "gate_box",
        "gate_value_big": "gate_value_big",
        "gate_caption": "gate_caption",
        "readout_box": "readout_box",
        "readout_text": "readout_text",
        "plot_handlers": "plot_handlers",
        "vline_gate": "vline_gate",
        "hline_h": "hline_h",
    }

    state = {
        "picked_dist": None,
    }

    def get_model():
        rw = Runway(
            elev=float(dpg.get_value(TAG["rw_elev"])),
            rdh=float(dpg.get_value(TAG["rw_rdh"])),
        )
        app = Approach(
            theta=float(dpg.get_value(TAG["theta"])),
            d=float(dpg.get_value(TAG["d"])),
        )
        return rw, app

    def refresh_plot():
        rw, app = get_model()
        max_km = float(dpg.get_value(TAG["plot_max_km"]))

        n = 250
        xs = [i * max_km / (n - 1) for i in range(n)]
        ys = [app.altitude(x, rw) for x in xs]

        dpg.set_value(TAG["line"], [xs, ys])

        y_min, y_max = min(ys), max(ys)
        pad = max(50.0, 0.08 * (y_max - y_min))
        dpg.set_axis_limits(TAG["x_axis"], 0.0, max_km)
        dpg.set_axis_limits(TAG["y_axis"], y_min - pad, y_max + pad)

        if state["picked_dist"] is not None:
            x = state["picked_dist"]
            x = max(0.0, min(max_km, x))
            y = app.altitude(x, rw)
            dpg.set_value(TAG["sel_point"], [[x], [y]])

    def update_readout(dist_km: float):
        rw, app = get_model()
        max_km = float(dpg.get_value(TAG["plot_max_km"]))
        dist_km = max(0.0, min(max_km, dist_km))

        y_on_ils = app.altitude(dist_km, rw)
        gate_dist = app.appgate(float(dpg.get_value(TAG["in_h"])), rw)

        dpg.set_value(
            TAG["readout_text"],
            f"Select Point:\n"
            f"Distance to Touchdown: {dist_km:.2f} km\n"
            f"Altitude:   {y_on_ils:.1f} m\n"
        )

        dpg.set_value(TAG["sel_point"], [[dist_km], [y_on_ils]])

    def recompute(sender=None, app_data=None, user_data=None):
        rw, app = get_model()

        h = float(dpg.get_value(TAG["in_h"]))
        dist = float(dpg.get_value(TAG["in_dist"]))

        gate_dist = app.appgate(h, rw)
        glide_alt = app.altitude(dist, rw)

        dpg.set_value(TAG["out_gate_dist"], f"{gate_dist:.2f} km")
        dpg.set_value(TAG["out_glide_alt"], f"{glide_alt:.1f} m")
        dpg.set_value(TAG["gate_value_big"], f"{gate_dist:.2f} km")

        refresh_plot()

        x0, x1 = dpg.get_axis_limits(TAG["x_axis"])
        y0, y1 = dpg.get_axis_limits(TAG["y_axis"])

        dpg.set_value(TAG["vline_gate"], gate_dist)
        dpg.set_value(TAG["hline_h"], h)

        if state["picked_dist"] is None:
            update_readout(dist)
        else:
            update_readout(state["picked_dist"])

    def on_plot_clicked(sender, app_data, user_data=None):
        if not dpg.is_item_hovered(TAG["plot"]):
            return

        mx, my = dpg.get_plot_mouse_pos()
        max_km = float(dpg.get_value(TAG["plot_max_km"]))
        if mx < 0.0 or mx > max_km:
            return

        state["picked_dist"] = mx

        dpg.set_value(TAG["in_dist"], float(mx))

        update_readout(mx)

    # ---------- DPG ----------
    dpg.create_context()
    dpg.create_viewport(title="Approach Gate Calculator", width=1280, height=800)

    dpg.set_viewport_small_icon("assets/app.ico")
    dpg.set_viewport_large_icon("assets/app.ico")
    # Fonts
    with dpg.font_registry():
        ui_font = dpg.add_font("C:/Windows/Fonts/segoeui.ttf", 18)
        big_font = dpg.add_font("C:/Windows/Fonts/segoeui.ttf", 48)
    dpg.bind_font(ui_font)

    # Themes
    with dpg.theme(tag="gate_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 30, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (255, 200, 0, 255))
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 2)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 10)

    with dpg.theme(tag="readout_theme"):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (24, 24, 24, 235))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (120, 160, 255, 255))
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 10)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 2)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)

    with dpg.window(
            tag="main_window",
            width=1260,
            height=-1,
            no_move=True,
            no_title_bar=True,
            no_resize=True,
            no_collapse=True,
    ):
        with dpg.group(tag="root_group", horizontal=True):

            # Left panel
            with dpg.child_window(tag="left_panel", width=600, height=-1):
                dpg.add_text("Parameters")
                dpg.add_separator()

                with dpg.child_window(tag=TAG["gate_box"], width=-1, height=130, border=True):
                    dpg.bind_item_theme(TAG["gate_box"], "gate_theme")
                    dpg.add_text(tag=TAG["gate_caption"], default_value="APP GATE (includes d)")
                    dpg.add_text(tag=TAG["gate_value_big"], default_value="0.00 km")
                    dpg.bind_item_font(TAG["gate_value_big"], big_font)
                    #dpg.bind_item_font(TAG["readout_text"], big_font)

                dpg.add_spacer(height=8)

                dpg.add_input_float(tag=TAG["rw_elev"], label="Runway elev (m)", default_value=initial_runway.elev, step=1.0, callback=recompute)
                dpg.add_input_float(tag=TAG["rw_rdh"], label="RDH (m)", default_value=initial_runway.rdh, step=1.0, callback=recompute)
                dpg.add_input_float(tag=TAG["theta"], label="Glide slope THETA (deg)", default_value=initial_app.theta, step=0.1, callback=recompute)
                dpg.add_input_float(tag=TAG["d"], label="Gate buffer d (km)", default_value=initial_app.d, step=0.1, callback=recompute)

                dpg.add_spacer(height=10)
                dpg.add_text("Conversions")
                dpg.add_separator()

                dpg.add_input_float(tag=TAG["in_h"], label="Height h (m)", default_value=900.0, step=10.0, callback=recompute)
                dpg.add_text("App gate distance:")
                dpg.add_text(tag=TAG["out_gate_dist"], default_value="0.00 km")

                dpg.add_spacer(height=6)
                dpg.add_input_float(tag=TAG["in_dist"], label="Distance to touchdown (km)", default_value=10.0, step=0.5, callback=recompute)
                dpg.add_text("ILS altitude at distance:")
                dpg.add_text(tag=TAG["out_glide_alt"], default_value="0.0 m")

                dpg.add_spacer(height=10)
                dpg.add_text("Plot")
                dpg.add_separator()
                dpg.add_input_float(tag=TAG["plot_max_km"], label="Plot range (km)", default_value=plot_max_km, step=1.0, callback=recompute)
                dpg.add_spacer(height=10)
                dpg.add_button(label="Recompute", callback=recompute)

            # Right panel
            with dpg.child_window(tag="right_panel", width=-1, height=-1):
                dpg.add_text("Glide Profile")
                dpg.add_spacer(height=4)

                with dpg.child_window(tag=TAG["readout_box"], width=-1, height=100, border=True):
                    dpg.bind_item_theme(TAG["readout_box"], "readout_theme")
                    dpg.add_text(tag=TAG["readout_text"], default_value="Select Point\nDistance to Touchdown: --\nAltitude: --")

                dpg.add_spacer(height=6)

                with dpg.plot(tag=TAG["plot"], height=-1, width=-1, no_menus=True, no_box_select=True):
                    dpg.add_plot_axis(dpg.mvXAxis, label="Distance to touchdown (km)", tag=TAG["x_axis"])
                    dpg.add_plot_axis(dpg.mvYAxis, label="Altitude (m)", tag=TAG["y_axis"])

                    dpg.add_line_series([0.0, 1.0], [0.0, 1.0], tag=TAG["line"], parent=TAG["y_axis"])
                    dpg.add_scatter_series([0.0], [0.0], tag=TAG["sel_point"], parent=TAG["y_axis"])

                    dpg.add_drag_line(
                        tag=TAG["vline_gate"],
                        default_value=0.0,
                        color=(255, 200, 0, 200),
                        thickness=2,
                        vertical=True,
                        show=True,
                    )

                    dpg.add_drag_line(
                        tag=TAG["hline_h"],
                        default_value=0.0,
                        color=(120, 160, 255, 200),
                        thickness=2,
                        vertical=False,
                        show=True,
                    )
                    dpg.configure_item(TAG["vline_gate"], no_inputs=True)
                    dpg.configure_item(TAG["hline_h"], no_inputs=True)

                with dpg.item_handler_registry(tag=TAG["plot_handlers"]):
                    dpg.add_item_clicked_handler(callback=on_plot_clicked)
                dpg.bind_item_handler_registry(TAG["plot"], TAG["plot_handlers"])

    dpg.set_primary_window("main_window", True)
    recompute()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
