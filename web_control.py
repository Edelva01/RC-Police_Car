"""Simple HTTP control server for browser-based vehicle commands."""

from config import WEB_PORT, WIFI_SETUP_AP_SSID
from wifi_setup import (
    connect_station,
    load_wifi_credentials,
    parse_form_body,
    save_wifi_credentials,
    stop_access_point,
    url_decode,
)



_HTML_PAGE = """<!doctype html>
<html>
<head>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <meta charset=\"utf-8\" />
    <title>Pico W Police Car</title>
    <style>
        body { font-family: sans-serif; margin: 16px; background: #f4f7fb; color: #1f2a44; }
        .card { max-width: 520px; margin: 0 auto; padding: 16px; background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,.08); }
        h1 { font-size: 1.2rem; margin: 0; }
        .brand {
            margin: 0 0 16px;
            padding: 0 0 14px;
            border-bottom: 2px solid #cbd5e1;
            background: #fff;
            color: #0f172a;
            box-shadow: none;
            border-radius: 0;
        }
        .brand-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .brand-title-wrap {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .brand-logo {
            width: 42px;
            height: 42px;
            object-fit: contain;
            border-radius: 8px;
            background: #f1f5f9;
            padding: 4px;
        }
        .brand-title {
            margin: 0;
            font-size: 1.15rem;
            line-height: 1.25;
        }
        .brand-turtleback {
            color: #1e3a8a;
            font-weight: 800;
            letter-spacing: 0.04em;
        }
        .brand-academy {
            color: #dc2626;
            font-weight: 700;
        }
        .brand-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.7rem;
            letter-spacing: 0.08em;
            font-weight: 700;
            background: #fee2e2;
            color: #dc2626;
        }
        .brand-subtitle {
            margin-top: 6px;
            font-size: 0.85rem;
            color: #2563eb;
            font-weight: 600;
        }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
        .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
        .grid-5 button { padding: 10px 6px; font-size: 0.85rem; }
        .grid-6 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
        button.police-on { background: #2563eb; }
        button.police-off { background: #64748b; }
        button.auto-on { background: #7c3aed; }
        button.auto-off { background: #64748b; }
        .cross {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: repeat(3, auto);
            gap: 8px;
            max-width: 360px;
            margin: 0 auto;
        }
        .cross-up { grid-column: 2; grid-row: 1; }
        .cross-left { grid-column: 1; grid-row: 2; }
        .cross-center { grid-column: 2; grid-row: 2; background: #0f766e; }
        .cross-right { grid-column: 3; grid-row: 2; }
        .cross-down { grid-column: 2; grid-row: 3; }
        button { padding: 10px; border: 0; border-radius: 8px; background: #2166f3; color: #fff; font-weight: 600; }
        button.stop { background: #d12f2f; }
        button.on { background: #1f9d49; }
        button.off { background: #d12f2f; }
        button.em-on { background: #e4a500; }
        button.em-off { background: #1f9d49; }
        .row { margin-top: 12px; }
        .gap-sm { margin-top: 16px; }
        .gap-lg { margin-top: 40px; }
        input[type=range] { width: 100%; }
        .status-panel {
            margin-top: 24px;
            padding: 12px 14px;
            border: 2px solid #93c5fd;
            border-radius: 10px;
            background: #eff6ff;
        }
        .status-label {
            margin: 0 0 6px;
            font-size: 0.8rem;
            font-weight: 700;
            color: #1d4ed8;
            letter-spacing: 0.03em;
        }
        #status {
            margin: 0;
            font-size: 0.95rem;
            word-break: break-word;
        }
        .status-distance {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #bfdbfe;
            font-size: 0.95rem;
            font-weight: 700;
            color: #1e3a8a;
        }
        .mode-banner {
            display: block;
            margin: 16px 0 0;
            padding: 10px 12px;
            border-radius: 10px;
            background: #eff6ff;
            border: 2px solid #93c5fd;
            color: #1e40af;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
        }
        .mode-banner:active { background: #dbeafe; }
        a.mode-banner.pico {
            background: #ecfdf5;
            border-color: #6ee7b7;
            color: #065f46;
        }
        .wifi-panel {
            margin-top: 28px;
            padding: 14px;
            border: 2px solid #fcd34d;
            border-radius: 10px;
            background: #fffbeb;
        }
        .wifi-panel h2 {
            margin: 0 0 6px;
            font-size: 1rem;
            color: #92400e;
        }
        .wifi-panel p { margin: 0 0 10px; font-size: 0.9rem; color: #78350f; }
        .wifi-panel label { display: block; margin: 10px 0 4px; font-weight: 600; }
        .wifi-panel input {
            width: 100%; box-sizing: border-box; padding: 10px;
            border: 1px solid #f59e0b; border-radius: 8px; font-size: 1rem;
        }
        .wifi-panel .wifi-submit {
            margin-top: 12px; width: 100%; padding: 12px; border: 0; border-radius: 8px;
            background: #d97706; color: #fff; font-weight: 700;
        }
        .wifi-hint { font-size: 0.8rem; color: #92400e; margin-top: 8px; }
        .wifi-msg { margin-bottom: 10px; padding: 8px 10px; border-radius: 8px; background: #eff6ff; }
        .wifi-msg.err { background: #fef2f2; color: #b91c1c; }
    </style>
</head>
<body>
    <div class=\"card\">
        <div class=\"brand\">
            <div class=\"brand-top\">
                <div class=\"brand-title-wrap\">
                    <img class=\"brand-logo\" src=\"https://turtlebackrobotics.com/assets/logomark-DZXyXXSX.png\" alt=\"Turtleback Robotics logo\" />
                    <h1 class=\"brand-title\">
                        <span class=\"brand-turtleback\">TURTLEBACK</span>
                        <span class=\"brand-academy\"> Robotics Academy</span>
                    </h1>
                </div>
                <span class=\"brand-badge\">ENROLLING NOW</span>
            </div>
            <div class=\"brand-subtitle\">Turn Screen Time Into Skill Time</div>
        </div>

        <div class=\"cross\">
            <button class=\"cross-up\" onclick=\"send('f')\">Forward Dir</button>
            <button class=\"cross-left\" onclick=\"send('l')\">Left</button>
            <button class=\"cross-center\" onclick=\"send('c')\">Center</button>
            <button class=\"cross-right\" onclick=\"send('r')\">Right</button>
            <button class=\"cross-down\" onclick=\"send('b')\">Reverse Dir</button>
        </div>

        <div class=\"row gap-sm\">
            <label>Speed: <span id=\"speedValue\">0</span></label>
            <input id=\"speed\" type=\"range\" min=\"0\" max=\"100\" value=\"0\" oninput=\"speedValue.textContent=this.value\" />
        </div>

        <div class=\"grid-2 row\">
            <button onclick=\"sendSpeed()\">Set Speed</button>
            <button onclick=\"send('s')\" class=\"stop\">Stop</button>
        </div>

        <div class=\"grid-6 gap-lg\">
            <button id=\"engineBtn\" onclick=\"toggleEngine()\">Engine</button>
            <button id=\"headlightBtn\" onclick=\"toggleHeadlight()\">Headlight</button>
            <button id=\"emergencyBtn\" onclick=\"toggleEmergency()\">Emergency</button>
            <button id=\"policeBtn\" class=\"police-off\" onclick=\"togglePolice()\">Police</button>
            <button id=\"autoBtn\" class=\"auto-off\" onclick=\"toggleAuto()\">Auto</button>
            <button onclick=\"refreshStatus()\">Refresh Status</button>
        </div>

        __WIFI_SETUP__

        <div class=\"status-panel\">
            <p class=\"status-label\">Car status</p>
            <div id=\"status\">Ready</div>
            <div class=\"status-distance\">Distance: <span id=\"distanceValue\">--</span> cm</div>
        </div>

        __MODE_BANNER__
    </div>

    <script>
        var requestQueue = [];
        var requestInFlight = false;
        var failCount = 0;
        var STATUS_POLL_MS = 2000;

        function markConnectionOk() {
            failCount = 0;
        }

        function markConnectionFail(statusEl, message) {
            failCount += 1;
            if (statusEl && failCount >= 2) {
                statusEl.textContent = message;
            }
        }

        function processRequestQueue() {
            if (requestInFlight || requestQueue.length === 0) {
                return;
            }

            var job = requestQueue.shift();
            requestInFlight = true;
            var settled = false;

            var xhr = new XMLHttpRequest();
            xhr.open('GET', job.url, true);
            xhr.timeout = 2500;
            xhr.setRequestHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
            xhr.setRequestHeader('Pragma', 'no-cache');
            xhr.setRequestHeader('Expires', '0');

            function complete(ok, responseText, errorStatus) {
                if (settled) {
                    return;
                }
                settled = true;

                if (ok) {
                    markConnectionOk();
                    if (job.onSuccess) {
                        job.onSuccess(responseText);
                    }
                } else if (job.onError) {
                    job.onError(errorStatus || 0);
                }

                requestInFlight = false;
                processRequestQueue();
            }

            xhr.onreadystatechange = function () {
                if (xhr.readyState !== 4) {
                    return;
                }

                if (xhr.status >= 200 && xhr.status < 300) {
                    complete(true, xhr.responseText, 0);
                    return;
                }

                complete(false, '', xhr.status || 0);
            };

            xhr.onerror = function () {
                complete(false, '', 0);
            };

            xhr.ontimeout = function () {
                complete(false, '', 0);
            };

            xhr.send(null);
        }

        function sendRequest(url, onSuccess, onError, priority) {
            var job = {
                url: url,
                onSuccess: onSuccess,
                onError: onError
            };

            // Commands jump the queue; drop older status polls so they cannot pile up.
            if (priority) {
                requestQueue = requestQueue.filter(function (item) {
                    return item.url.indexOf('/status') < 0;
                });
                requestQueue.unshift(job);
            } else if (url.indexOf('/status') >= 0) {
                var hasStatus = requestQueue.some(function (item) {
                    return item.url.indexOf('/status') >= 0;
                });
                if (hasStatus || requestInFlight) {
                    return;
                }
                requestQueue.push(job);
            } else {
                requestQueue.push(job);
            }

            processRequestQueue();
        }

        function send(cmd) {
            var statusEl = document.getElementById('status');
            var url = '/command?cmd=' + encodeURIComponent(cmd) + '&_ts=' + Date.now();

            sendRequest(
                url,
                function () {
                    if (statusEl) {
                        statusEl.textContent = 'sent: ' + cmd + ' @ ' + new Date().toLocaleTimeString();
                    }
                    refreshStatusSafe();
                },
                function () {
                    markConnectionFail(statusEl, 'car not responding - check power and Wi-Fi');
                },
                true
            );
        }

        function refreshStatusSafe() {
            fetchStatus(function () {
                var statusEl = document.getElementById('status');
                markConnectionFail(statusEl, 'car not responding - check power and Wi-Fi');
            });
        }

        function syncHeadlightButton(statusText) {
            var btn = document.getElementById('headlightBtn');
            if (!btn) return;

            if (statusText.indexOf('headlights=on') >= 0) {
                btn.classList.remove('off');
                btn.classList.add('on');
                btn.textContent = 'Headlight ON';
                return;
            }

            btn.classList.remove('on');
            btn.classList.add('off');
            btn.textContent = 'Headlight OFF';
        }

        function syncEngineButton(statusText) {
            var btn = document.getElementById('engineBtn');
            if (!btn) return;

            if (statusText.indexOf('engine=on') >= 0) {
                btn.classList.remove('off');
                btn.classList.add('on');
                btn.textContent = 'Engine ON';
                return;
            }

            btn.classList.remove('on');
            btn.classList.add('off');
            btn.textContent = 'Engine OFF';
        }

        function syncEmergencyButton(statusText) {
            var btn = document.getElementById('emergencyBtn');
            if (!btn) return;

            if (statusText.indexOf('emergency=on') >= 0) {
                btn.classList.remove('em-off');
                btn.classList.add('em-on');
                btn.textContent = 'Emergency ON';
                return;
            }

            btn.classList.remove('em-on');
            btn.classList.add('em-off');
            btn.textContent = 'Emergency OFF';
        }

        function syncPoliceButton(statusText) {
            var btn = document.getElementById('policeBtn');
            if (!btn) return;

            btn.textContent = 'Police';

            if (statusText.indexOf('police=on') >= 0) {
                btn.classList.remove('police-off');
                btn.classList.add('police-on');
                return;
            }

            btn.classList.remove('police-on');
            btn.classList.add('police-off');
        }

        function syncAutoButton(statusText) {
            var btn = document.getElementById('autoBtn');
            if (!btn) return;

            btn.textContent = 'Auto';

            if (statusText.indexOf('auto=on') >= 0) {
                btn.classList.remove('auto-off');
                btn.classList.add('auto-on');
                return;
            }

            btn.classList.remove('auto-on');
            btn.classList.add('auto-off');
        }

        function syncDistanceFromStatus(statusText) {
            var el = document.getElementById('distanceValue');
            if (!el) return;

            var marker = 'distance=';
            var markerIndex = statusText.indexOf(marker);
            if (markerIndex < 0) {
                el.textContent = '--';
                return;
            }

            var start = markerIndex + marker.length;
            var end = statusText.indexOf(',', start);
            var value = (end >= 0 ? statusText.slice(start, end) : statusText.slice(start)).trim();
            el.textContent = value || '--';
        }

        function toggleHeadlight() {
            send('h');
        }

        function toggleEngine() {
            send('eng');
        }

        function toggleEmergency() {
            send('e');
        }

        function togglePolice() {
            send('p');
        }

        function toggleAuto() {
            send('auto');
        }

        function sendSpeed() {
            var v = document.getElementById('speed').value;
            send(v);
        }

        function fetchStatus(onError) {
            sendRequest(
                '/status?_ts=' + Date.now(),
                function (txt) {
                    var statusEl = document.getElementById('status');
                    if (statusEl) {
                        statusEl.textContent = txt;
                    }
                    syncHeadlightButton(txt);
                    syncEngineButton(txt);
                    syncEmergencyButton(txt);
                    syncPoliceButton(txt);
                    syncAutoButton(txt);
                    syncDistanceFromStatus(txt);
                },
                onError
            );
        }

        window.send = send;
        window.toggleHeadlight = toggleHeadlight;
        window.toggleEngine = toggleEngine;
        window.toggleEmergency = toggleEmergency;
        window.togglePolice = togglePolice;
        window.toggleAuto = toggleAuto;
        window.sendSpeed = sendSpeed;
        window.refreshStatus = refreshStatusSafe;

        refreshStatusSafe();
        setInterval(refreshStatusSafe, STATUS_POLL_MS);
    </script>
</body>
</html>
"""

_WIFI_PAGE = """<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset="utf-8" />
    <title>Change Wi-Fi</title>
    <style>
        body { font-family: sans-serif; margin: 16px; background: #f4f7fb; color: #1f2a44; }
        .card { max-width: 520px; margin: 0 auto; padding: 16px; background: #fff;
                border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,.08); }
        h1 { font-size: 1.1rem; margin: 0 0 8px; color: #1e3a8a; }
        p { margin: 0 0 12px; color: #475569; font-size: 0.95rem; }
        label { display: block; margin: 10px 0 4px; font-weight: 600; }
        input { width: 100%; box-sizing: border-box; padding: 10px; border: 1px solid #cbd5e1;
                border-radius: 8px; font-size: 1rem; }
        button { margin-top: 14px; width: 100%; padding: 12px; border: 0; border-radius: 8px;
                 background: #2166f3; color: #fff; font-weight: 700; font-size: 1rem; }
        .back { display: inline-block; margin-bottom: 12px; color: #1d4ed8; font-weight: 600; }
        .msg { margin-bottom: 12px; padding: 10px; border-radius: 8px; background: #eff6ff; }
        .err { background: #fef2f2; color: #b91c1c; }
    </style>
</head>
<body>
    <div class="card">
        <a class="back" href="/">&larr; Back to drive</a>
        <h1>Change Wi-Fi</h1>
        <p>Current: Wi-Fi "__CURRENT_SSID__"</p>
        __WIFI_MESSAGE__
        <form method="POST" action="/wifi/save">
            <label for="ssid">Wi-Fi name (SSID)</label>
            <input id="ssid" name="ssid" type="text" maxlength="32" required autocomplete="off" />
            <label for="password">Wi-Fi password</label>
            <input id="password" name="password" type="password" maxlength="64" autocomplete="off" />
            <button type="submit">Save and Connect</button>
        </form>
    </div>
</body>
</html>
"""


class WebController:
    def __init__(self, state):
        self.state = state
        self.network = None
        self.socket = None
        self.ip_address = None
        self.wifi_mode = "sta"
        self.current_ssid = ""
        self._wifi_form_message = ""
        self._wifi_form_is_error = False

    def start(self, wifi_mode="sta", ip_address=None):
        """Bind the control HTTP server on STA or Pico AP."""

        try:
            import network
            import socket
        except ImportError:
            print("Web control unavailable: network/socket modules not found")
            return False

        self.network = network
        self.wifi_mode = wifi_mode if wifi_mode in ("sta", "ap") else "sta"

        if ip_address:
            self.ip_address = ip_address
        elif self.wifi_mode == "ap":
            ap = network.WLAN(network.AP_IF)
            if not ap.active():
                print("Web control unavailable: Pico AP is not active")
                return False
            self.ip_address = ap.ifconfig()[0]
        else:
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("Web control unavailable: Wi-Fi is not connected")
                return False
            self.ip_address = wlan.ifconfig()[0]

        self.current_ssid = self._read_current_ssid()

        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", WEB_PORT))
        server.listen(4)
        server.setblocking(False)

        self.socket = server

        if self.wifi_mode == "ap":
            print("Drive + setup ready at http://%s:%d (Pico Wi-Fi)" % (self.ip_address, WEB_PORT))
        else:
            print("Web control ready at http://%s:%d" % (self.ip_address, WEB_PORT))
        return True

    def stop(self):
        if self.socket is not None:
            try:
                self.socket.close()
            except OSError:
                pass
            self.socket = None

    def _escape_html(self, value):
        text = str(value or "")
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _read_current_ssid(self):
        if self.wifi_mode == "ap":
            return WIFI_SETUP_AP_SSID

        try:
            wlan = self.network.WLAN(self.network.STA_IF)
            ssid = wlan.config("essid")
            if ssid:
                return str(ssid)
        except (OSError, AttributeError, TypeError, ValueError):
            pass

        saved_ssid, _ = load_wifi_credentials()
        return saved_ssid or "unknown"

    def _build_status_text(self):
        direction_text = "forward" if self.state.direction == 1 else "reverse"
        mode_text = "pico-wifi" if self.wifi_mode == "ap" else "home-wifi"

        if self.state.distance_cm is None:
            distance_text = "--"
        else:
            distance_text = "%.1f" % self.state.distance_cm

        return (
            "mode=%s, speed=%d, direction=%s, steering=%d, emergency=%s, police=%s, auto=%s, headlights=%s, engine=%s, distance=%s"
            % (
                mode_text,
                self.state.speed,
                direction_text,
                self.state.steering_angle,
                "on" if self.state.emergency_lights_active else "off",
                "on" if self.state.police_lights_enabled else "off",
                "on" if self.state.self_driving_enabled else "off",
                "on" if self.state.headlights_enabled else "off",
                "on" if self.state.engine_enabled else "off",
                distance_text,
            )
        )

    def _build_mode_banner(self):
        ssid = self._escape_html(self.current_ssid or self._read_current_ssid())
        css_class = "mode-banner pico" if self.wifi_mode == "ap" else "mode-banner"
        return (
            '<a class="%s" href="/wifi">Connected: Wi-Fi &quot;%s&quot;</a>'
            % (css_class, ssid)
        )

    def _build_html_page(self):
        return (
            _HTML_PAGE
            .replace("__MODE_BANNER__", self._build_mode_banner())
            .replace("__WIFI_SETUP__", "")
        )

    def _build_wifi_page(self):
        if self._wifi_form_message:
            css = "msg err" if self._wifi_form_is_error else "msg"
            message_html = '<div class="%s">%s</div>' % (css, self._wifi_form_message)
        else:
            message_html = ""

        ssid = self._escape_html(self.current_ssid or self._read_current_ssid())
        return (
            _WIFI_PAGE
            .replace("__CURRENT_SSID__", ssid)
            .replace("__WIFI_MESSAGE__", message_html)
        )

    def _respond(self, client, status_code, content_type, body):
        try:
            if content_type == "text/html":
                content_type = "text/html; charset=utf-8"
            elif content_type == "text/plain":
                content_type = "text/plain; charset=utf-8"

            payload = body
            if isinstance(payload, str):
                payload = payload.encode("utf-8")

            header = (
                "HTTP/1.1 %d OK\r\n"
                "Content-Type: %s\r\n"
                "Content-Length: %d\r\n"
                "Connection: close\r\n\r\n"
            ) % (status_code, content_type, len(payload))

            client.send(header)

            total_sent = 0
            while total_sent < len(payload):
                sent = client.send(payload[total_sent:])
                if sent is None or sent <= 0:
                    break
                total_sent += sent
        except OSError:
            pass

    def _extract_path(self, path_or_line):
        """Return the URL path without query string from a path or request line."""

        parts = path_or_line.split(" ")
        if len(parts) >= 2 and parts[0].upper() in ("GET", "POST", "HEAD", "PUT", "DELETE"):
            path = parts[1]
        elif parts:
            path = parts[0]
        else:
            path = "/"

        query_index = path.find("?")
        if query_index >= 0:
            return path[:query_index]
        return path

    def _url_decode(self, value):
        return url_decode(value)

    def _extract_cmd(self, path_with_query):
        marker = "cmd="
        index = path_with_query.find(marker)
        if index < 0:
            return None

        cmd = path_with_query[index + len(marker) :]
        amp_index = cmd.find("&")
        if amp_index >= 0:
            cmd = cmd[:amp_index]

        return self._url_decode(cmd).strip().lower()

    def _read_http_request(self, client):
        """Read one HTTP request; return (method, full_path, body_text) or None."""

        client.settimeout(0.5)
        request_bytes = client.recv(2048)
        if not request_bytes:
            return None

        request_text = request_bytes.decode("utf-8", "ignore")
        header_text, sep, body_text = request_text.partition("\r\n\r\n")
        if not sep:
            body_text = ""

        content_length = 0
        for line in header_text.split("\r\n")[1:]:
            lower = line.lower()
            if lower.startswith("content-length:"):
                try:
                    content_length = int(line.split(":", 1)[1].strip())
                except ValueError:
                    content_length = 0
                break

        body_bytes = body_text.encode("utf-8") if body_text else b""
        while len(body_bytes) < content_length:
            try:
                chunk = client.recv(content_length - len(body_bytes))
            except OSError:
                break
            if not chunk:
                break
            body_bytes += chunk

        if content_length > 0:
            body_text = body_bytes[:content_length].decode("utf-8", "ignore")

        request_line = header_text.split("\r\n", 1)[0]
        parts = request_line.split(" ")
        method = parts[0].upper() if parts else "GET"
        full_path = parts[1] if len(parts) > 1 else "/"
        return method, full_path, body_text

    def _handle_wifi_save(self, client, body_text):
        """Save credentials and try joining the requested Wi-Fi network."""

        fields = parse_form_body(body_text)
        ssid = fields.get("ssid", "")
        password = fields.get("password", "")

        ok, message = save_wifi_credentials(ssid, password)
        if not ok:
            self._wifi_form_message = message
            self._wifi_form_is_error = True
            self._respond(client, 400, "text/html", self._build_wifi_page())
            return

        joined, result = connect_station(ssid, password)
        if not joined:
            self._wifi_form_message = "Could not join that Wi-Fi. Check the name and password."
            self._wifi_form_is_error = True
            print("Join Wi-Fi failed:", result)
            self._respond(client, 200, "text/html", self._build_wifi_page())
            return

        if self.wifi_mode == "ap":
            stop_access_point()

        self.wifi_mode = "sta"
        self.ip_address = result
        self.current_ssid = ssid.strip()
        self._wifi_form_message = ""
        self._wifi_form_is_error = False

        done_page = (
            "<!doctype html><html><head><meta charset='utf-8' />"
            "<meta name='viewport' content='width=device-width, initial-scale=1' /></head>"
            "<body style='font-family:sans-serif;margin:24px'>"
            "<h1>Connected</h1>"
            "<p>Connected: Wi-Fi \"%s\"</p>"
            "<p>On that Wi-Fi network, open:</p>"
            "<p><a href='http://%s/'>http://%s/</a></p>"
            "<p><a href='/'>Back to drive</a> (works if you are already on that network)</p>"
            "</body></html>"
        ) % (self._escape_html(self.current_ssid), result, result)
        self._respond(client, 200, "text/html", done_page)
        print("Switched to Wi-Fi control at http://%s/" % result)

    def _handle_client(self, client):
        """Serve one HTTP request. Return a driver command when present."""

        try:
            parsed = self._read_http_request(client)
            if parsed is None:
                return None

            method, full_path, body_text = parsed
            path = self._extract_path(full_path)

            if method == "POST" and path.startswith("/wifi/save"):
                self._handle_wifi_save(client, body_text)
                return None

            if path.startswith("/wifi"):
                self._wifi_form_message = ""
                self._wifi_form_is_error = False
                self._respond(client, 200, "text/html", self._build_wifi_page())
                return None

            if path.startswith("/command"):
                cmd = self._extract_cmd(full_path)
                if cmd is None or cmd == "":
                    self._respond(client, 400, "text/plain", "missing cmd")
                    return None

                self._respond(client, 200, "text/plain", "ok")
                return cmd

            if path.startswith("/status"):
                self._respond(client, 200, "text/plain", self._build_status_text())
                return None

            self._respond(client, 200, "text/html", self._build_html_page())
            return None

        except OSError:
            return None

        finally:
            try:
                client.close()
            except OSError:
                pass

    def poll_for_command(self):
        """Accept pending clients; return the first command found this pass."""

        if self.socket is None:
            return None

        command = None
        for _ in range(4):
            try:
                client, _ = self.socket.accept()
            except OSError:
                break

            result = self._handle_client(client)
            if command is None and result is not None:
                command = result

        return command
