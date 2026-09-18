"""
Fixed demo topology for the first shared demonstration.

Keep these identifiers exactly in sync with the database, dashboard and
SMS templates - the team brief is explicit that the demo must use the
same identifiers everywhere.
"""

from simulator.models import Site

UPLINK_MUKONO = "uplink-mukono"

SITES = {
    "site-mukono-central": Site(
        site_id="site-mukono-central",
        name="Mukono Central",
        depends_on=[UPLINK_MUKONO],
    ),
    "site-ucu-area": Site(
        site_id="site-ucu-area",
        name="UCU Area",
        depends_on=[UPLINK_MUKONO],
    ),
    "site-seeta": Site(
        site_id="site-seeta",
        name="Seeta",
        depends_on=[UPLINK_MUKONO],
    ),
}


def sites_sharing_dependency(dependency_id: str):
    return [s for s in SITES.values() if dependency_id in s.depends_on]