import socket
import threading
import sys
import pyfiglet
import requests
import json
from datetime import datetime
from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

console = Console()

# Optional API key file for GeoIP
file_path_setting = "settings.json"

# GeoIP Lookup Function
def geo_lookup(ip_address):
    try:
        with open(file_path_setting, "r") as file:
            api_key = json.load(file).get("api_key_geo")
            url = f"https://ipinfo.io/{ip_address}?token={api_key}" if api_key else f"https://ipinfo.io/{ip_address}/json"
    except FileNotFoundError:
        url = f"https://ipinfo.io/{ip_address}/json"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        geo_data = {
            "IP Address": ip_address,
            "City": data.get("city", "N/A"),
            "Region": data.get("region", "N/A"),
            "Country": data.get("country", "N/A"),
            "Postal": data.get("postal", "N/A"),
            "Coordinates": data.get("loc", "N/A"),
            "Timezone": data.get("timezone", "N/A"),
            "Organization": data.get("org", "N/A"),
            "Hostname": data.get("hostname", "N/A"),
        }

        table = Table(title="GeoIP Information")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        for key, value in geo_data.items():
            table.add_row(key, value)

        console.print(table)

    except requests.RequestException as e:
        console.print(f"[bold red]GeoIP Lookup Failed:[/bold red] {e}")


# Subdomain Enumeration Function
def enumerate_subdomains(domain, wordlist=None):
    console.print("\n[bold magenta]Enumerating Subdomains...[/bold magenta]")

    if not wordlist:
        wordlist = ["www", "mail", "ftp", "dev", "test", "api", "blog", "ns1", "ns2"]

    table = Table(title="Subdomain Enumeration Results")
    table.add_column("Subdomain", style="cyan")
    table.add_column("Resolved IP", style="green")

    for sub in wordlist:
        subdomain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(subdomain)
            table.add_row(subdomain, ip)
        except socket.gaierror:
            continue

    console.print(table)


# Banner
print(Fore.RED + "-" * 70 + Style.RESET_ALL)
banner = pyfiglet.figlet_format("PORTSCANNER")
print(Fore.RED + Style.BRIGHT + banner + Style.RESET_ALL)
console.print("[bold green]\t\t\tBY VINAYAK RAJ[/bold green]")
print(Fore.RED + "-" * 70 + Style.RESET_ALL)

# Host input and resolution
target = input(Fore.BLUE + "Enter Host To Scan (Domain OR IP): " + Style.RESET_ALL)
try:
    host = socket.gethostbyname(target)
except socket.gaierror:
    print(Fore.RED + "Unable to resolve Hostname.\nExiting..." + Style.RESET_ALL)
    sys.exit()

print(Fore.BLUE + f"TARGET: {target}" + Style.RESET_ALL)
print(Fore.BLUE + f"HOST IP: {host}" + Style.RESET_ALL)

start_time = datetime.now()
print("START TIME :", start_time.strftime("%d-%m-%Y %H:%M:%S"))
print(Fore.YELLOW + "-" * 70 + Style.RESET_ALL)

# Banner Grabbing Function
def grab_banner(ip, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode(errors="ignore").strip()
        sock.close()
        return banner if banner else "No banner"
    except:
        return "No banner"

# Port Scanning Function
def scan_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "UNKNOWN"
            banner = grab_banner(host, port)
            print(Fore.GREEN + f"PORT {port} OPEN | SERVICE: {service} | BANNER: {banner}" + Style.RESET_ALL)
        sock.close()
    except Exception as e:
        print(Fore.RED + f"Error scanning port {port}: {e}" + Style.RESET_ALL)

# Start port scanning
threads = []
for port in range(1, 1025):
    thread = threading.Thread(target=scan_port, args=(port,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

# GeoIP + Subdomains
print(Fore.YELLOW + "-" * 70 + Style.RESET_ALL)
geo_lookup(host)
print(Fore.YELLOW + "-" * 70 + Style.RESET_ALL)
enumerate_subdomains(target)

# End summary
end_time = datetime.now()
elapsed = end_time - start_time
print(Fore.YELLOW + "-" * 70 + Style.RESET_ALL)
print("END TIME :", end_time.strftime("%H:%M:%S"))
print("TIME ELAPSED :", elapsed)
print(Fore.RED + "-" * 70 + Style.RESET_ALL)
