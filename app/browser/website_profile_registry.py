import json
from pathlib import Path


PROFILE_DIR = Path(__file__).parent / "website_profiles"


def profile_exists(site_name: str) -> bool:
    return (PROFILE_DIR / f"{site_name}.json").exists()


def load_website_profile(site_name: str) -> dict:
    path = PROFILE_DIR / f"{site_name}.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Website profile not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_website_profile(site_name: str, profile: dict) -> None:
    PROFILE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = PROFILE_DIR / f"{site_name}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            profile,
            file,
            indent=2,
        )


def get_or_discover_website_profile(site_name: str, discover_func):
    if profile_exists(site_name):
        return load_website_profile(site_name)

    profile = discover_func(site_name)

    if not profile:
        raise RuntimeError(
            f"Could not discover website profile for {site_name}"
        )

    save_website_profile(site_name, profile)

    return profile