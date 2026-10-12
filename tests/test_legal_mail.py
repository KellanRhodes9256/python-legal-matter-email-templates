from src.legal_mail import InfraiClient, Matter, lifecycle_templates


def test_deadline_template_contains_matter_decision() -> None:
    matter = Matter("M-7", "Riley", "riley@example.com", "2026-12-01")
    templates = lifecycle_templates(matter)
    deadline = next(item for item in templates if item.name.endswith("deadline-follow-up"))
    assert deadline.template_vars["deadline"] == "2026-12-01"
    assert "2026-12-01" in deadline.html


def test_template_request_fields() -> None:
    client = InfraiClient(api_key="test")
    requests = []
    client._request = lambda method, path, payload: requests.append((method, path, payload)) or {}
    template = lifecycle_templates(Matter("M-7", "Riley", "riley@example.com", "2026-12-01"))[0]

    client.create_template(template)
    client.preview_template("template-id", template.template_vars)

    assert requests[0][2] == {
        "name": template.name,
        "subject": template.subject,
        "html": template.html,
        "default_vars": {"client_name": "Riley"},
    }
    assert requests[1][2] == {"vars": {"client_name": "Riley"}}
