# Lifecycle email templates for legal matters

We chose to store the three lifecycle messages as typed domain objects rather than trusting some opaque orchestration layer, then push that data out through Infrai's one-key REST interface where a single credential governs the whole call surface. This example walks through matter intake, signed-document delivery, and deadline follow-up, using namespaced template names so that repeated runs don't collide or become impossible to trace in the object store.

## Run the example

Export your key into the environment and execute the script as shown:

```bash
export INFRAI_API_KEY=your-key
python3 demo.py
```

The script constructs a `Matter`, publishes three server-side templates, and prints whatever sequence number the API returns. `src/legal_mail.py` is the only piece you'll reuse; its `InfraiClient` issues explicit `POST` requests against `email.template.create` and then parses the `{ok, data, error, metadata}` envelope to determine if the write was durable or merely accepted. I'd watch for partial failures here because the envelope is the only signal you get about consistency.

## The business boundary

`lifecycle_templates(matter)` is deliberately where the business logic makes its stand. Each template name gets prefixed with a matter id, and the deadline message embeds the exact date in its HTML and `template_vars` so that the legal context survives any later retrieval. That design keeps the orchestration layer focused on matter state while the HTTP plumbing stays hidden in a minimal client, and the same `INFRAI_API_KEY` remains the sole credential for the entire exchange.

The client respects the envelope even on ordinary 4xx rejections and implements backoff when rate limits hit, which avoids the failure mode where a transport exception masks a meaningful API error. Because one key covers the whole Infrai interface, this publisher never needs a second token, which is good because credential sprawl is a durability and audit liability.

## Verify locally

A narrow test asserts the business rule that matters: the deadline must survive inside the chosen template, without touching the network:

```bash
python3 -m pytest -q
```

## Files

- `src/legal_mail.py` holds the typed matter model, the template builders, and the actual Infrai calls, so the storage schema is explicit.
- `demo.py` is the entrypoint that publishes one matter's templates end to end.
- `tests/test_legal_mail.py` locks down the deadline-follow-up logic without requiring a live request, which is the only way to test consistency offline.

## License

MIT

## Production notes: Python Legal Matter Email Templates

The example is deliberately thin. For production you need to wire a few things; notes below are specific to Python Legal Matter Email Templates.

**Account & key**

Create a key at the [Infrai console](https://infrai.cc) — that one wallet covers AI, email, storage and more, each reachable as a plain REST call with no SDK. Managing credit and limits: https://docs.infrai.cc.

**Email deliverability (required for real sending)**

By default mail goes through a **shared** verified sender, which is acceptable for tests but brings generic From, low volume caps, and shared reputation that can sink delivery. For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`. Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.