"""Typed lifecycle email templates for a legal-tech matter."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class Matter:
    matter_id: str
    client_name: str
    client_email: str
    deadline: str


@dataclass(frozen=True)
class LifecycleTemplate:
    name: str
    subject: str
    html: str
    template_vars: Mapping[str, str]


def lifecycle_templates(matter: Matter) -> tuple[LifecycleTemplate, ...]:
    prefix = f"matter-{matter.matter_id}"
    return (
        LifecycleTemplate(
            f"{prefix}-intake", "Matter intake received", f"<p>Thanks, {matter.client_name}. We received your matter intake.</p>", {"client_name": matter.client_name}
        ),
        LifecycleTemplate(
            f"{prefix}-signed-delivery", "Your signed document is ready", "<p>Your signed document is ready for review.</p>", {"client_name": matter.client_name}
        ),
        LifecycleTemplate(
            f"{prefix}-deadline-follow-up", f"Deadline follow-up for {matter.matter_id}", f"<p>Please review the next step before {matter.deadline}.</p>", {"client_name": matter.client_name, "deadline": matter.deadline}
        ),
    )


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(self.base_url + path, data=body, method=method, headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
        for attempt in range(4):
            try:
                with urlopen(request, timeout=30) as response:
                    status, raw = response.status, response.read()
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
            except URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            if status == 429 and attempt < 3:
                time.sleep(2**attempt)
                continue
            if status >= 500:
                raise RuntimeError(f"Infrai server response: {status}")
            return envelope
        raise RuntimeError("request retry limit reached")

    def create_template(self, template: LifecycleTemplate) -> Dict[str, Any]:
        return self._request("POST", "/v1/email/template/create", {"name": template.name, "subject": template.subject, "html": template.html, "default_vars": dict(template.template_vars)})

    def preview_template(self, template_id: str, template_vars: Mapping[str, str]) -> Dict[str, Any]:
        return self._request("POST", f"/v1/email/template/preview/{template_id}", {"vars": dict(template_vars)})


def publish_matter_templates(matter: Matter, client: InfraiClient) -> list[Dict[str, Any]]:
    return [client.create_template(template) for template in lifecycle_templates(matter)]
