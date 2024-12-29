import os
import socket
import ipaddress
import requests
from scapy.all import sr1, IP, ICMP
from bs4 import BeautifulSoup
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor

# Validate IP Address
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# Ping Sweep
def ping_sweep(target_ip):
    """Check if the target is alive using ICMP ping."""
    if not is_valid_ip(target_ip):
        print("[-] Invalid IP address. Please try again.")
        return False

    print(f"Pinging {target_ip}...")
    try:
        icmp_request = sr1(IP(dst=target_ip)/ICMP(), timeout=2, verbose=0)
        if icmp_request:
            print(f"[+] {target_ip} is reachable.")
            return True
        else:
            print(f"[-] {target_ip} is not reachable.")
            return False
    except Exception as e:
        print(f"[-] Error during ping sweep: {e}")
        return False

# OS Detection
def os_detection(target_ip):
    """Detect the target OS using TTL analysis."""
    if not is_valid_ip(target_ip):
        print("[-] Invalid IP address. Please try again.")
        return

    print("\nRunning OS detection...")
    ttl_guess = {
        range(60, 65): "Linux/Unix",
        range(120, 130): "Windows",
        range(250, 256): "Cisco/Networking Device"
    }

    try:
        icmp_request = sr1(IP(dst=target_ip)/ICMP(), timeout=2, verbose=0)
        if icmp_request:
            ttl = icmp_request.ttl
            os_type = "Unknown"
            for ttl_range, os_name in ttl_guess.items():
                if ttl in ttl_range:
                    os_type = os_name
                    break
            print(f"[+] Detected OS from TTL: {os_type} (TTL={ttl})")
        else:
            print("[-] ICMP request failed; OS detection inconclusive.")
    except Exception as e:
        print(f"[-] OS detection error: {e}")

# Port Scan
def port_scan(target_ip, start_port=1, end_port=1024, max_threads=100):
    """Perform a thread-limited port scan with optional banner grabbing."""
    if not is_valid_ip(target_ip):
        print("[-] Invalid IP address. Please try again.")
        return []

    print(f"\nScanning ports {start_port}-{end_port} on {target_ip}...")
    open_ports = []

    def scan_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    banner = "Unknown"
                    try:
                        sock.send(b"HEAD / HTTP/1.1\r\n\r\n")
                        banner = sock.recv(1024).decode(errors="ignore").strip()
                    except Exception:
                        banner = "Open (no banner)"
                    open_ports.append({"Port": port, "Banner": banner})
        except Exception:
            pass

    with ThreadPoolExecutor(max_threads) as executor:
        for port in range(start_port, end_port + 1):
            executor.submit(scan_port, port)

    print("\n[+] Port Scan Results:")
    print(tabulate(open_ports, headers="keys", tablefmt="grid"))
    return open_ports

# Exploit-DB Search
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


import textwrap
from tabulate import tabulate

def search_cve_mitre(query, output_file="mitre_cve_results.txt"):
    """
    Search for CVEs on MITRE CVE database for the given query.
    """
    print(f"\nSearching MITRE CVE database for '{query}'...")
    base_url = "https://cve.mitre.org/cgi-bin/cvekey.cgi"
    params = {"keyword": query}

    try:
        # Fetch the response
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the table explicitly
        div_table = soup.find("div", {"id": "TableWithRules"})
        if not div_table:
            print("[DEBUG] Div with ID 'TableWithRules' not found.")
            return

        table = div_table.find("table")
        if not table:
            print("[DEBUG] Table inside 'TableWithRules' not found.")
            return

        # Locate rows in the table
        rows = table.find_all("tr")[1:]  # Skip header row
        if not rows:
            print("[-] No data rows found in the table.")
            return

        # Parse each row and collect results
        results = []
        for row in rows:
            columns = row.find_all("td")
            if len(columns) >= 2:
                cve_id = columns[0].text.strip()
                cve_link = f"https://cve.mitre.org{columns[0].find('a')['href']}"
                description = columns[1].text.strip()

                # Truncate description for console output
                truncated_description = (description[:80] + "...") if len(description) > 80 else description

                # Fix URLs to avoid duplicates
                if cve_link.startswith("https://cve.mitre.orghttps://"):
                    cve_link = cve_link.replace("https://cve.mitre.org", "")

                results.append([cve_id, truncated_description, cve_link])

        # Display only the first 10 results in the console
        headers = ["CVE ID", "Description", "Link"]
        print("\n" + tabulate(results[:10], headers=headers, tablefmt="fancy_grid"))

        # Save full results to a file
        with open(output_file, "w", encoding="utf-8") as file:
            for row in results:
                file.write(f"{row[0]}: {row[1]} ({row[2]})\n")

        print(f"\n[+] Found {len(results)} CVEs. Displaying the first 10 above.")
        print(f"[+] All results have been saved to {output_file}.")

    except requests.exceptions.RequestException as e:
        print(f"[-] Error querying MITRE CVE database: {e}")
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")





# Main Menu
def menu():
    art = R"""
 /$$$$$$$                                          /$$  /$$$$$$          
| $$__  $$                                        |__/ /$$__  $$         
| $$  \ $$  /$$$$$$   /$$$$$$$  /$$$$$$  /$$$$$$$  /$$| $$  \__//$$   /$$
| $$$$$$$/ /$$__  $$ /$$_____/ /$$__  $$| $$__  $$| $$| $$$$   | $$  | $$
| $$__  $$| $$$$$$$$| $$      | $$  \ $$| $$  \ $$| $$| $$_/   | $$  | $$
| $$  \ $$| $$_____/| $$      | $$  | $$| $$  | $$| $$| $$     | $$  | $$
| $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$/| $$  | $$| $$| $$     |  $$$$$$$
|__/  |__/ \_______/ \_______/ \______/ |__/  |__/|__/|__/      \____  $$
                                                                /$$  | $$
                                                               |  $$$$$$/
                                                                \______/ 
"""
    print(art)
    print("The recon toolbox.")

    while True:
        print("\nRecon Tool Menu")
        print("1. Ping Sweep")
        print("2. OS Detection")
        print("3. Port Scan")
        print("4. Search CVEs")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            target_ip = input("Enter the target IP address: ").strip()
            ping_sweep(target_ip)
        elif choice == "2":
            target_ip = input("Enter the target IP address: ").strip()
            os_detection(target_ip)
        elif choice == "3":
            target_ip = input("Enter the target IP address: ").strip()
            start_port = int(input("Enter the starting port (default 1): ") or 1)
            end_port = int(input("Enter the ending port (default 1024): ") or 1024)
            port_scan(target_ip, start_port, end_port)
        elif choice == "4":
            query = input("Enter the CVE search term (e.g., 'Apache 2.4', 'OpenSSH'): ").strip()
            search_cve_mitre(query)
        elif choice == "5":
            print("Exiting the tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Main Function
def main():
    menu()

if __name__ == "__main__":
    main()
