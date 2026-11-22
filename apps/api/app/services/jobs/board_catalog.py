from dataclasses import dataclass

from app.config import get_settings


@dataclass(frozen=True)
class BoardRef:
    source_type: str
    key: str
    name: str


# Public board slugs. Greenhouse and Lever have no global job index; each company
# board is fetched separately via their public APIs.
_GREENHOUSE = [
    ("airbnb", "Airbnb"),
    ("anthropic", "Anthropic"),
    ("asana", "Asana"),
    ("atlassian", "Atlassian"),
    ("cloudflare", "Cloudflare"),
    ("coinbase", "Coinbase"),
    ("databricks", "Databricks"),
    ("datadog", "Datadog"),
    ("discord", "Discord"),
    ("doordash", "DoorDash"),
    ("dropbox", "Dropbox"),
    ("duolingo", "Duolingo"),
    ("figma", "Figma"),
    ("gitlab", "GitLab"),
    ("grammarly", "Grammarly"),
    ("hashicorp", "HashiCorp"),
    ("hubspot", "HubSpot"),
    ("instacart", "Instacart"),
    ("linear", "Linear"),
    ("lyft", "Lyft"),
    ("mongodb", "MongoDB"),
    ("notion", "Notion"),
    ("nvidia", "NVIDIA"),
    ("openai", "OpenAI"),
    ("palantir", "Palantir"),
    ("pinterest", "Pinterest"),
    ("reddit", "Reddit"),
    ("robinhood", "Robinhood"),
    ("shopify", "Shopify"),
    ("snowflake", "Snowflake"),
    ("spacex", "SpaceX"),
    ("spotify", "Spotify"),
    ("stripe", "Stripe"),
    ("twilio", "Twilio"),
    ("vercel", "Vercel"),
    ("zendesk", "Zendesk"),
]

_LEVER = [
    ("airtable", "Airtable"),
    ("box", "Box"),
    ("brex", "Brex"),
    ("checkr", "Checkr"),
    ("compass", "Compass"),
    ("coursera", "Coursera"),
    ("eventbrite", "Eventbrite"),
    ("flexport", "Flexport"),
    ("gusto", "Gusto"),
    ("hopper", "Hopper"),
    ("mixpanel", "Mixpanel"),
    ("netflix", "Netflix"),
    ("opendoor", "Opendoor"),
    ("postman", "Postman"),
    ("scaleai", "Scale AI"),
    ("sourcegraph", "Sourcegraph"),
    ("thumbtack", "Thumbtack"),
    ("twitch", "Twitch"),
    ("wayfair", "Wayfair"),
    ("zapier", "Zapier"),
]


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_board_catalog(
    *,
    greenhouse_tokens: str | None = None,
    lever_sites: str | None = None,
    include_defaults: bool = True,
) -> list[BoardRef]:
    settings = get_settings()
    extra_gh = (
        greenhouse_tokens if greenhouse_tokens is not None else settings.greenhouse_board_tokens
    )
    extra_lever = lever_sites if lever_sites is not None else settings.lever_sites

    boards: dict[tuple[str, str], BoardRef] = {}
    if include_defaults:
        for key, name in _GREENHOUSE:
            boards[("greenhouse", key.lower())] = BoardRef("greenhouse", key.lower(), name)
        for key, name in _LEVER:
            boards[("lever", key.lower())] = BoardRef("lever", key.lower(), name)
    for key in _parse_csv(extra_gh):
        boards[("greenhouse", key.lower())] = BoardRef("greenhouse", key.lower(), key)
    for key in _parse_csv(extra_lever):
        boards[("lever", key.lower())] = BoardRef("lever", key.lower(), key)
    return list(boards.values())
