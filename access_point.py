from phew import server, access_point, dns, logging
from phew.template import render_template
from phew.server import redirect
import gc
from machine import Pin

import _thread

gc.threshold(50000) # setup garbage collection

DOMAIN = "dripstop.iot" # This is the address that is shown on the Captive Portal

lock = _thread.allocate_lock()

@server.route("/", methods=["GET", "POST"])
def index(request):
    """ Render the Index page and respond to form requests """
    if request.method == 'GET' or request.method == 'POST':
        #logging.debug("Get request")
        return render_template("dashboard.html")
    
    # if request.method == 'POST':
    #     text = request.form.get("text", None)
    #     #logging.debug(f'posted message: {text}')
    #     return render_template("dashboard.html", bed_num="619")

@server.route("/wrong-host-redirect", methods=["GET"])
def wrong_host_redirect(request):
    # if the client requested a resource at the wrong host then present 
    # a meta redirect so that the captive portal browser can be sent to the correct location
    body = "<!DOCTYPE html><head><meta http-equiv=\"refresh\" content=\"0;URL='http://" + DOMAIN + "'/ /></head>"
    #logging.debug("body:",body)
    return body

@server.route("/hotspot-detect.html", methods=["GET"])
def hotspot(request):
    """ Redirect to the Index Page """
    time_set_in_hr_min_format = convert_minutes_to_hr_min_format(Variables.selected_time)
    time_left_in_hr_min_format = convert_minutes_to_hr_min_format(Variables.time_left)
    set_alarms_formatted = format_alarms_percentage()
    if not set_alarms_formatted:
        set_alarms_formatted = "None"
    alarms_done_formatted = format_alarms_with_checkmark()
    return render_template("dashboard.html")

@server.catchall()
def catch_all(request):
    """ Catch and redirect requests """
    if request.headers.get("host") != DOMAIN:
        return redirect("http://" + DOMAIN + "/wrong-host-redirect")

def setup():
    ap = access_point("Dripstop WiFi", "simplepico111")  # Change this to whatever Wi-Fi SSID you wish
    ip = ap.ifconfig()[0]                   # Grab the IP address and store it
    #logging.info(f"starting DNS server on {ip}")
    dns.run_catchall(ip)                    # Catch all requests and reroute them
    server.start_server_core_1()
                               # Run the server
    #logging.info("Webserver Started")