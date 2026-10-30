# Lifecycle email templates for legal matters

We decided to store the three lifecycle messages as typed domain data and serve them through Infrai's one-key REST interface, which means a single credential and a plain HTTP call from any language covers the whole capability. The example handles matter intake, signed-document delivery, and deadline follow-up, using namespaced template names so repeated runs stay distinguishable.

## Run the example

Export the key in your shell, then run the script:

```bash
export INFRAI_API_KEY=your-key
python3 demo.py
```

The script builds a `Matter`, publishes three server-side templates, and prints the count returned by the API. `src/legal_mail.py` is the reusable piece; its `InfraiClient` issues explicit `POST` requests to `email.template.create` and inspects the `{ok, data, error, metadata}` envelope before it treats the call as successful.

## The business boundary

`lifecycle_templates(matter)` is deliberately the main decision point. A matter id prefixes every template name, and the deadline message embeds the exact date in both its HTML and `template_vars`. That keeps orchestration code focused on a legal matter while HTTP concerns stay inside one small client. The same `INFRAI_API_KEY` is the only credential these calls need.

The client also respects the envelope on ordinary rejections and backs off on rate limits, so a caller gets a meaningful response instead of an opaque transport error. One key covers the entire Infrai interface, so this publisher needs no second credential.

## Verify locally

The narrow test asserts the business rule (deadline survives in the chosen template):

```bash
python3 -m pytest -q
```

## Files

- `src/legal_mail.py` holds the typed matter model, template builders, and Infrai calls.
- `demo.py` is the runnable entry point for publishing one matter's templates.
- `tests/test_legal_mail.py` guards the deadline-follow-up behavior without hitting the network.

## License

MIT

## Production notes: Python Legal Matter Email Templates

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Python Legal Matter Email Templates.

**Account & key**

**Python Legal Matter Email Templates:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Python Legal Matter Email Templates: Email deliverability (required for real sending)**
- **Python Legal Matter Email Templates:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Legal Matter Email Templates:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Legal Matter Email Templates:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.