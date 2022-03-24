import plotly.offline as pyo

HTML_STYLE = """
<style>
    body {background-color: #00050F;}
    div  {display: inline-block; margin: 2px; padding:2px;}
    h1 {font-size: 3em; color: floralwhite; font-family: 'Courier New', monospace}
    h2 {font-size: 2em; color: floralwhite; font-family: 'Courier New', monospace; margin-bottom: 2px}
    .container { white-space: nowrap; }

    /* light mode stuff */
    /* background */
    body.light {background-color: floralwhite;}
    /* title */
    .light h1, .light h2 {color: #00050F;} 
    /* graph background */
    .light svg.main-svg:first-child {background: #F5F5F5 !important;}
    /* info layer */
    .light .infolayer .bg {fill: #F5F5F5 !important;}

    /* text */
     .light text {fill: #00050F !important;}

    /* label text */
    .light .gtitle,
    .light .xtitle,
    .light .ytitle,
    .light .annotation-text,
    .light .legendtitletext,
    .light .legendtext {fill: #00050F !important;}
</style>
"""


def figures_to_html(
    imu_plots, baro_plots, accelerometer_plots, magneto_plots, state_plots, filename
):
    """Saves a list of plotly figures in an html file."""

    dashboard = open(filename, "w")
    head = f"""<html><head>{HTML_STYLE}<button onclick="body.classList.toggle('light');">Light/Dark</button></head><body><center>\n"""
    dashboard.write(head)

    #         span {
    #             float: left;
    #             white-space:nowrap;
    #         }

    
    dashboard.write("<h1>State Estimation Data</h1>")
    
    add_js = True
    xyz = ["AGL Altitude & Height", "Velocity", "Acceleration"]
    i = 0
    for fig in state_plots:
        inner_html = pyo.plot(fig, include_plotlyjs=add_js, output_type="div")
        dashboard.write(f'<h2>{xyz[i]}</h2><div class="container">')
        dashboard.write(inner_html)
        dashboard.write("</div>")
        add_js = False
        i += 1

    dashboard.write("<br/>")

    dashboard.write("<h1>IMU Data - Acceleration</h1>")
    # dashboard.write('<h1>IMU Data - Acceleration</h1><div class="container">')

    xyz = "XYZ"
    i = 0
    for fig in imu_plots[:3]:
        inner_html = pyo.plot(fig, include_plotlyjs=add_js, output_type="div")
        dashboard.write(f'<h2>Acc {xyz[i]}</h2><div class="container">')
        dashboard.write(inner_html)
        dashboard.write("</div>")
        add_js = False
        i += 1

    dashboard.write("<br/>")

    i = 0
    dashboard.write("<h1>IMU Data - Gyros</h1>")
    for fig in imu_plots[3:]:
        inner_html = pyo.plot(fig, include_plotlyjs=add_js, output_type="div")
        dashboard.write(f'<h2>Gyro {xyz[i]}</h2><div class="container">')
        dashboard.write(inner_html)
        dashboard.write("</div>")
        add_js = False
        i += 1

    dashboard.write("<br/>")

    dashboard.write("<h1>Barometer Data</h1>")
    xyz = ["Temperature", "Pressure"]
    i = 0
    for fig in baro_plots:
        inner_html = pyo.plot(fig, include_plotlyjs=add_js, output_type="div")
        dashboard.write(f'<h2>{xyz[i]}</h2><div class="container">')
        dashboard.write(inner_html)
        dashboard.write("</div>")
        add_js = False
        i += 1

    dashboard.write("<br/>")

    dashboard.write("<h1>Accelerometer Data</h1>")
    xyz = "XYZ"
    i = 0
    for fig in accelerometer_plots:
        inner_html = pyo.plot(fig, include_plotlyjs=add_js, output_type="div")
        dashboard.write(f'<h2>Accelerometer {xyz[i]}</h2><div class="container">')
        dashboard.write(inner_html)
        dashboard.write("</div>")
        add_js = False
        i += 1

    dashboard.write("<br/>")

    dashboard.write("<h1>Magnetometer Data</h1>")
    xyz = "XYZ"
    i = 0
    for fig in magneto_plots:
        inner_html = pyo.plot(fig, include_plotlyjs=add_js, output_type="div")
        dashboard.write(f'<h2>Magneto {xyz[i]}</h2><div class="container">')
        dashboard.write(inner_html)
        dashboard.write("</div>")
        add_js = False
        i += 1

    dashboard.write("<br/>")

    dashboard.write("</center></body></html>" + "\n")
