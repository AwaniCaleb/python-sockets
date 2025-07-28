from scanner import PortScanner


def main():
    # Create an instance of PortScanner and scan a specific port
    scanner = PortScanner()
    scanner.scan_port(9999)


if __name__ == "__main__":
    main()
