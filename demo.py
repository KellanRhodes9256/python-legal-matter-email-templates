from src.legal_mail import InfraiClient, Matter, publish_matter_templates


def main() -> None:
    matter = Matter("M-1042", "Avery Chen", "avery@example.com", "2026-10-15")
    results = publish_matter_templates(matter, InfraiClient())
    print(f"published {len(results)} lifecycle templates")


if __name__ == "__main__":
    main()
