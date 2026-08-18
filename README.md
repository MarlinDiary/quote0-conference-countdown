# Quote/0 Conference Countdown

A deliberately minimal conference deadline display for a 296×152 Quote/0
e-ink screen. It shows exactly one conference name and the number of days left.

## Change the target conference

Edit only [`conference.yml`](conference.yml):

```yaml
name: SANER 2027
deadline: 2026-09-25
```

The file accepts exactly two fields. `deadline` is interpreted as the end of
that date in Anywhere on Earth (AoE, UTC-12). `Days Left` is calculated using
calendar dates in `Pacific/Auckland`, including the Auckland-local date on which
the AoE deadline occurs. The Railway worker reads the raw
GitHub file again before every render, so committing an edit is enough even
when Railway is not connected to the repository for automatic deployments.

The initial deadline is the SANER 2027 Research Track paper submission date
from the [official call for papers](https://conf.researchr.org/track/saner-2027/saner-2027-papers).

## Preview locally

```bash
uv sync
uv run python render.py
```

The preview defaults to `/tmp/conference-countdown.png`.

## Run continuously

```bash
uv run python display.py --loop
```

Required Railway secrets for device pushes:

- `QUOTE_API_KEY`
- `QUOTE_DEVICE_ID`

Keep `QUOTE_PUSH_ENABLED=false` until the second Quote/0 has an Image API item
in its loop. Set it to `true` after one preview and one explicit test push have
been verified. Secrets remain in Railway and never enter `conference.yml`.

The worker renders every three hours by default. It downloads and validates the
public `conference.yml` before each render. Changing that GitHub file and
committing it is the only normal maintenance operation.

## Verification

```bash
uv run python -m unittest discover -s tests -v
docker build -t quote0-conference-countdown .
```

## Stop device writes

From the linked Railway checkout:

```bash
./scripts/disable-railway-push.sh
```
