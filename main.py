from flask import Flask, render_template, request
import socket
import os
import platform
import requests

app = Flask(__name__)

def check_dns(domain):
    """Cek apakah domain bisa di-resolve ke IP"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None

def check_ping(domain):
    """Cek apakah host merespons ping"""
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    response = os.system(f"ping {param} {domain} > nul 2>&1" if platform.system().lower() == "windows" else f"ping {param} {domain} > /dev/null 2>&1")
    return response == 0

def check_http(url):
    """Cek apakah website bisa diakses via HTTP"""
    if not url.startswith("http"):
        url = "http://" + url
    try:
        response = requests.get(url, timeout=5)
        return True, response.status_code
    except requests.exceptions.RequestException:
        return False, None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        domain = request.form.get("url").strip().replace("https://", "").replace("http://", "").split("/")[0]

        dns_ok, ip = check_dns(domain)
        ping_ok = check_ping(domain) if dns_ok else False
        http_ok, http_code = check_http(domain)

        result = {
            "domain": domain,
            "ip": ip if dns_ok else "-",
            "dns": "✅ OK" if dns_ok else "❌ Gagal",
            "ping": "✅ Bisa diping" if ping_ok else "❌ Tidak merespons",
            "http": f"✅ Aktif ({http_code})" if http_ok else "❌ Tidak merespons HTTP"
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
