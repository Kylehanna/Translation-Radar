# Source Inventory

## Technology Publisher

As of 2026-05-09, Translation Radar tracks a starter Technology Publisher inventory based on passive DNS host discovery plus spot verification of page titles.

Current direct-host probe result:
- 41 institution or brand hosts probed
- 34 hosts resolved directly on the institution-native Technology Publisher site
- 7 hosts were unresolved in this pass due to `404` or timeout behavior

Current preferred sourcing rule:
- prefer the institution-native Technology Publisher catalog URL when it resolves
- use Canberra or other aggregate RSS only as a secondary discovery and backfill layer
- infer institution attribution from direct host assets, contact emails, and item metadata when using aggregate feeds

Current observed host count:
- 42 unique `technologypublisher.com` hosts, including the root marketing site

Rough active institution or brand endpoint estimate:
- 35 to 45 active institution-facing endpoints

Why this is a rough count:
- passive DNS can include aliases, redirects, and inactive historical hosts
- some hosts represent brands or offices rather than institutions
- some institutions may sit on custom domains or unobserved subdomains and therefore be missed

The tracked inventory is stored in:
- `data/source_inventory/technologypublisher_hosts.csv`

The current API can expose this inventory at:
- `GET /sources/registry/technologypublisher`

The next step after this inventory baseline is to verify feed or page patterns host by host and assign a parser strategy for each source.

## AUTM Coverage Target

Translation Radar now treats the AUTM 2022 US Licensing Activity Survey respondent roster as an explicit coverage target.

Current AUTM roster source in this repo:
- `data/source_inventory/autm_2022_institutions.txt`

Current API surface for coverage tracking:
- `GET /sources/coverage/autm-2022`

Current Canberra retirement rule:
- keep Canberra only while AUTM respondent coverage is incomplete at the direct institution-native layer
- remove Canberra from the catalog-family registry once AUTM respondent direct coverage reaches 100%
- do not treat Canberra as a primary source when a verified direct institutional catalog exists

## Other Catalog Families

Translation Radar should not assume Technology Publisher is the whole market.

Additional source families now tracked conceptually in the registry:
- Wellspring Sophia
- Custom university catalogs
- Canberra aggregate feeds

Current API surfaces for source preference logic:
- `POST /sources/resolve/preferred-catalog`
- `POST /sources/fetch/preferred-catalog`

Recommended priority order:
1. Institution-native Technology Publisher catalogs
2. Institution-native Wellspring or custom catalogs
3. Canberra or other aggregate RSS feeds for discovery, backfill, and cross-checking

Current Wellspring baseline:
- confirmed product family: `https://www.wellspring.com/sophia`
- confirmed institution-side software instance: `https://swcatalog.umd.edu/well-spring-sophia`
- full public commercialization-catalog host inventory for Wellspring is still pending