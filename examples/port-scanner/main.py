from scanner import PortScanner


def main():
    # Create an instance of PortScanner
    scanner = PortScanner()

    # Scan a range of ports
    scanner.scan_range()


if __name__ == "__main__":
    main()
