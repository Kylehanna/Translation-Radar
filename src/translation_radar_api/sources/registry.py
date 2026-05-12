from __future__ import annotations

from csv import DictReader
from pathlib import Path

from translation_radar_api.models import (
    CampusFamilyRegistryEntry,
    CampusFamilyRegistrySummary,
    InstitutionCoverageEntry,
    InstitutionCoverageSummary,
    OrganizationFamilyCoverageEntry,
    OrganizationFamilyCoverageSummary,
    SourceCatalogFamilyEntry,
    SourceCatalogFamilySummary,
    SourceRegistryEntry,
    SourceRegistrySummary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "data" / "source_inventory"
TECHNOLOGY_PUBLISHER_REGISTRY = DATA_ROOT / "technologypublisher_hosts.csv"
AUTM_2018_INSTITUTIONS = DATA_ROOT / "autm_2018_institutions.txt"
AUTM_2022_INSTITUTIONS = DATA_ROOT / "autm_2022_institutions.txt"
CAMPUS_FAMILY_REGISTRY = DATA_ROOT / "campus_family_registry.csv"

_TECHNOLOGY_PUBLISHER_PROBE_STATUS: dict[str, dict[str, str]] = {
    "arizona.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://arizona.technologypublisher.com/site/search"},
    "bakeridi.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://bakeridi.technologypublisher.com/site/search"},
    "binghamton.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://binghamton.technologypublisher.com/site/search"},
    "broadinstitute.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://broadinstitute.technologypublisher.com/site/search"},
    "cedars-sinai.technologypublisher.com": {"access_status": "unverified-404", "preferred_url": "", "notes_suffix": "Direct host probe returned 404 on root and /site/search"},
    "chopbreakthroughs.technologypublisher.com": {"access_status": "unverified-404", "preferred_url": "", "notes_suffix": "Direct host probe returned 404 on root and /site/search"},
    "dit.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://dit.technologypublisher.com/site/search"},
    "emoryott.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://emoryott.technologypublisher.com/site/search"},
    "gwu.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://gwu.technologypublisher.com/site/search"},
    "ilo.technologypublisher.com": {"access_status": "unverified-404", "preferred_url": "", "notes_suffix": "Direct host probe returned 404 on root and /site/search"},
    "jeffott.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://jeffott.technologypublisher.com/site/search"},
    "jhu.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://jhu.technologypublisher.com/site/search"},
    "kingsbusiness.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://kingsbusiness.technologypublisher.com/site/search"},
    "lehighott.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://lehighott.technologypublisher.com/site/search"},
    "neu.technologypublisher.com": {"access_status": "unverified-404", "preferred_url": "", "notes_suffix": "Direct host probe returned 404 on root and /site/search"},
    "notredametech.technologypublisher.com": {"access_status": "unverified-404", "preferred_url": "", "notes_suffix": "Direct host probe returned 404 on root and /site/search"},
    "ohsu.technologypublisher.com": {"access_status": "unverified-timeout", "preferred_url": "", "notes_suffix": "Direct host probe timed out on root and /site/search"},
    "oregonstate.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://oregonstate.technologypublisher.com/site/search"},
    "puotl.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://puotl.technologypublisher.com/site/search"},
    "rochester.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://rochester.technologypublisher.com/site/search"},
    "rutgers.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://rutgers.technologypublisher.com/site/search"},
    "sc.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://sc.technologypublisher.com/site/search"},
    "skoltech.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://skoltech.technologypublisher.com/site/search"},
    "southalabama.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://southalabama.technologypublisher.com/site/search"},
    "stevens.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://stevens.technologypublisher.com/site/search"},
    "stfc.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://stfc.technologypublisher.com/site/search"},
    "sttm.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://sttm.technologypublisher.com/site/search"},
    "tbdo.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://tbdo.technologypublisher.com/site/search"},
    "ua.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://ua.technologypublisher.com/site/search"},
    "uaf.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://uaf.technologypublisher.com/site/search"},
    "uclb.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://uclb.technologypublisher.com/site/search"},
    "ufinnovate.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://ufinnovate.technologypublisher.com/site/search"},
    "uchicago.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://uchicago.technologypublisher.com/site/search"},
    "upenn.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://upenn.technologypublisher.com/site/search"},
    "usp.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://usp.technologypublisher.com/site/search"},
    "utah.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://utah.technologypublisher.com/site/search", "notes_suffix": "Root title suggests redirect or stale branding; search endpoint still resolves"},
    "utdallas.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://utdallas.technologypublisher.com/site/search"},
    "uthealth.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://uthealth.technologypublisher.com/site/search"},
    "utoledo.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://utoledo.technologypublisher.com/site/search"},
    "utrf.technologypublisher.com": {"access_status": "verified-direct", "preferred_url": "https://utrf.technologypublisher.com/site/search"},
    "worldiscoveries.technologypublisher.com": {"access_status": "unverified-404", "preferred_url": "", "notes_suffix": "Direct host probe returned 404 on root and /site/search"},
    "www.technologypublisher.com": {"access_status": "marketing-root", "preferred_url": "https://www.technologypublisher.com/"},
}

_AUTM_DIRECT_SOURCE_ALIASES: dict[str, list[str]] = {
    "Princeton University": ["PU OTL"],
    "Rutgers, The State University of New Jersey": ["Rutgers University"],
    "University of Arizona": ["Tech Launch Arizona"],
    "University of South Carolina": ["SC"],
    "University of Tennessee": ["UTRF"],
}

_PUBLIC_CATALOG_OVERRIDES: dict[str, dict[str, str]] = {
    "harvarduniversity": {
        "institution_name": "Harvard University",
        "host": "otd.harvard.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://otd.harvard.edu/industry-investors/commercialization-opportunities/",
        "search_url": "https://otd.harvard.edu/industry-investors/commercialization-opportunities/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Commercialization Opportunities | Harvard Office of Technology Development",
        "notes": "Institution-native public commercialization opportunities catalog override.",
    },
    "johnshopkinsuniversity": {
        "institution_name": "Johns Hopkins University",
        "host": "ventures.jhu.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://ventures.jhu.edu/innovations/technologies/",
        "search_url": "https://ventures.jhu.edu/innovations/technologies/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Technologies | Johns Hopkins Technology Ventures",
        "notes": "Institution-native public commercialization catalog override preferred over Technology Publisher host.",
    },
    "johnshopkinsuniversityappliedphysicslaboratory": {
        "institution_name": "Johns Hopkins University Applied Physics Laboratory",
        "host": "www.jhuapl.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://www.jhuapl.edu/tech-transfer/technologies-patents",
        "search_url": "https://www.jhuapl.edu/tech-transfer/technologies-patents",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Technologies & Patents | JHUAPL Tech Transfer",
        "notes": "Institution-native public technology and patents catalog override.",
    },
    "arizonastateuniversity": {
        "institution_name": "Arizona State University",
        "host": "skysong.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://skysong.technologypublisher.com/",
        "search_url": "https://skysong.technologypublisher.com/advancedsearch",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Technology Portal | Arizona Technology Enterprises",
        "notes": "Institution-native public Arizona State University technology catalog override.",
    },
    "massachusettsinstituteoftechnology": {
        "institution_name": "Massachusetts Institute of Technology",
        "host": "tlo.mit.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://tlo.mit.edu/industry-entrepreneurs/available-technologies",
        "search_url": "https://tlo.mit.edu/industry-entrepreneurs/available-technologies",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Browse Technologies | MIT Technology Licensing Office",
        "notes": "Institution-native public available technologies catalog override.",
    },
    "brownuniversity": {
        "institution_name": "Brown University",
        "host": "brown.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://brown.technologypublisher.com/",
        "search_url": "https://brown.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Search Commercial Opportunities | Brown University",
        "notes": "Institution-native public Brown commercial opportunities catalog override.",
    },
    "bostonuniversity": {
        "institution_name": "Boston University",
        "host": "bu.flintbox.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://bu.flintbox.com/",
        "search_url": "https://bu.flintbox.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Technologies for License | Boston University",
        "notes": "Institution-native public Flintbox technologies catalog for Boston University.",
    },
    "casewesternreserveuniversity": {
        "institution_name": "Case Western Reserve University",
        "host": "case.portals.in-part.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://case.portals.in-part.com/",
        "search_url": "https://case.portals.in-part.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Case Western Reserve University | Inpart",
        "notes": "Institution-native public available intellectual property portal for Case Western Reserve University.",
    },
    "carnegiemellonuniversity": {
        "institution_name": "Carnegie Mellon University",
        "host": "cmu.flintbox.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "http://cmu.flintbox.com/",
        "search_url": "http://cmu.flintbox.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Technologies | Carnegie Mellon University",
        "notes": "Institution-native public Carnegie Mellon technology catalog via Flintbox.",
    },
    "cedarssinaimedicalcenter": {
        "institution_name": "Cedars-Sinai Medical Center",
        "host": "cedars.flintbox.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://cedars.flintbox.com/",
        "search_url": "https://cedars.flintbox.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies | Cedars-Sinai",
        "notes": "Institution-native public Cedars-Sinai technology portfolio linked from Technology Ventures.",
    },
    "childrenshospitalboston": {
        "institution_name": "Children's Hospital Boston",
        "host": "bch.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://bch.technologypublisher.com/",
        "search_url": "https://bch.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Search Technologies | Boston Children's Hospital",
        "notes": "Institution-native public technology catalog for Children's Hospital Boston linked from TIDO Tech Search.",
    },
    "columbiauniversity": {
        "institution_name": "Columbia University",
        "host": "inventions.techventures.columbia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://inventions.techventures.columbia.edu/categories",
        "search_url": "https://inventions.techventures.columbia.edu/search",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Search technologies - Columbia Technology Ventures",
        "notes": "Institution-native public inventions catalog for Columbia Technology Ventures.",
    },
    "cornelluniversity": {
        "institution_name": "Cornell University",
        "host": "cornell.flintbox.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://cornell.flintbox.com/",
        "search_url": "https://cornell.flintbox.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Technologies | Cornell University",
        "notes": "Institution-native public Cornell technology catalog via Flintbox.",
    },
    "georgiainstituteoftechnology": {
        "institution_name": "Georgia Institute of Technology",
        "host": "licensing.research.gatech.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://licensing.research.gatech.edu/technologies",
        "search_url": "https://licensing.research.gatech.edu/technologies",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Technologies | Office of Technology Licensing",
        "notes": "Institution-native public technology listing for Georgia Tech Office of Technology Licensing.",
    },
    "danafarbercancerinstitute": {
        "institution_name": "Dana-Farber Cancer Institute",
        "host": "innovations.dana-farber.org",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://innovations.dana-farber.org/",
        "search_url": "https://innovations.dana-farber.org/our-technologies/therapeutics/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Innovation for Impact | Dana-Farber",
        "notes": "Institution-native public Dana-Farber innovations portal with public technology listings.",
    },
    "fredhutchinsoncancercenter": {
        "institution_name": "Fred Hutchinson Cancer Center",
        "host": "www.fredhutch.org",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://www.fredhutch.org/en/investors/business-development/available-technologies.html",
        "search_url": "https://www.fredhutch.org/en/investors/business-development/available-technologies.html",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies | Fred Hutch",
        "notes": "Institution-native public Fred Hutch available technologies page for business development.",
    },
    "michiganstateuniversity": {
        "institution_name": "Michigan State University",
        "host": "msut.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://msut.technologypublisher.com/",
        "search_url": "https://msut.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Available Technologies | Michigan State University",
        "notes": "Institution-native public MSU Technologies catalog override.",
    },
    "hleemoffittcancercenterresearchinstitute": {
        "institution_name": "H. Lee Moffitt Cancer Center & Research Institute",
        "host": "moffitt.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://moffitt.technologypublisher.com/",
        "search_url": "https://moffitt.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Technology Search | Moffitt",
        "notes": "Institution-native public Moffitt technology catalog via Inteum Technology Publisher.",
    },
    "northwesternuniversity": {
        "institution_name": "Northwestern University",
        "host": "inventions.invo.northwestern.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://inventions.invo.northwestern.edu/",
        "search_url": "https://inventions.invo.northwestern.edu/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Search Available Technologies | Northwestern INVO",
        "notes": "Institution-native public available technologies catalog override.",
    },
    "purdueresearchfoundation": {
        "institution_name": "Purdue Research Foundation",
        "host": "licensing.prf.org",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://licensing.prf.org/",
        "search_url": "https://licensing.prf.org/products",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Explore Purdue Technologies Available for Licensing",
        "notes": "Institution-native public Purdue Research Foundation licensing catalog.",
    },
    "newyorkuniversity": {
        "institution_name": "New York University",
        "host": "license.tov.med.nyu.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://license.tov.med.nyu.edu/",
        "search_url": "https://license.tov.med.nyu.edu/products",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Find Technology Opportunities | NYU",
        "notes": "Institution-native public technology opportunities catalog for NYU.",
    },
    "northcarolinastateuniversity": {
        "institution_name": "North Carolina State University",
        "host": "ncsu.portals.in-part.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://ncsu.portals.in-part.com/",
        "search_url": "https://ncsu.portals.in-part.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "North Carolina State University | Inpart",
        "notes": "Institution-native public invention portal for North Carolina State University.",
    },
    "stanforduniversity": {
        "institution_name": "Stanford University",
        "host": "techfinder.stanford.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techfinder.stanford.edu/",
        "search_url": "https://techfinder.stanford.edu/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Explore Stanford technologies available for licensing",
        "notes": "Institution-native public Stanford technology catalog override.",
    },
    "universityofcincinnati": {
        "institution_name": "University of Cincinnati",
        "host": "uc.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://uc.technologypublisher.com/",
        "search_url": "https://uc.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "University of Cincinnati Available Technologies",
        "notes": "Institution-native public University of Cincinnati available technologies catalog via 1819 Innovation Hub.",
    },
    "cincinnatichildrenshospitalmedicalcenter": {
        "institution_name": "Cincinnati Children's Hospital Medical Center",
        "host": "www.cincinnatichildrens.org",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://www.cincinnatichildrens.org/research/support/innovation-ventures/",
        "search_url": "https://www.cincinnatichildrens.org/research/support/innovation-ventures/technologies",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Innovation Ventures | Cincinnati Children's",
        "notes": "Institution-native public Innovation Ventures portal with searchable technology database.",
    },
    "thesalkinstituteforbiologicalstudies": {
        "institution_name": "The Salk Institute for Biological Studies",
        "host": "salk.portals.in-part.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://salk.portals.in-part.com/",
        "search_url": "https://salk.portals.in-part.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Salk Institute for Biological Studies | Inpart",
        "notes": "Institution-native public available technology portal for the Salk Institute.",
    },
    "universityofcalifornialosangeles": {
        "institution_name": "University of California, Los Angeles",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=LA",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=LA",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies | UCLA",
        "notes": "Institution-native public UC available technologies catalog override for UCLA.",
    },
    "universityofcaliforniaberkeley": {
        "institution_name": "University of California, Berkeley",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=BK",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=BK",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California, Berkeley",
        "notes": "Institution-native public UC available technologies catalog override for Berkeley.",
    },
    "universityofcaliforniairvine": {
        "institution_name": "University of California, Irvine",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=IR",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=IR",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California, Irvine",
        "notes": "Institution-native public UC available technologies catalog override for Irvine.",
    },
    "universityofcaliforniamerced": {
        "institution_name": "University of California, Merced",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=MC",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=MC",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California, Merced",
        "notes": "Institution-native public UC available technologies catalog override for Merced.",
    },
    "universityofcaliforniariverside": {
        "institution_name": "University of California, Riverside",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=RV",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=RV",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California, Riverside",
        "notes": "Institution-native public UC available technologies catalog override for Riverside.",
    },
    "universityofcaliforniasandiego": {
        "institution_name": "University of California, San Diego",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SD",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SD",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California, San Diego",
        "notes": "Institution-native public UC available technologies catalog override for San Diego.",
    },
    "universityofcaliforniasanfrancisco": {
        "institution_name": "University of California, San Francisco",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SF",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SF",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from UCSF",
        "notes": "Institution-native public UC available technologies catalog override for UCSF.",
    },
    "universityofcaliforniasantabarbara": {
        "institution_name": "University of California, Santa Barbara",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SB",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SB",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California, Santa Barbara",
        "notes": "Institution-native public UC available technologies catalog override for Santa Barbara.",
    },
    "universityofcaliforniasantacruz": {
        "institution_name": "University of California, Santa Cruz",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SC",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default?campus=SC",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California, Santa Cruz",
        "notes": "Institution-native public UC available technologies catalog override for Santa Cruz.",
    },
    "universityofcaliforniasystem": {
        "institution_name": "University of California System",
        "host": "techtransfer.universityofcalifornia.edu",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://techtransfer.universityofcalifornia.edu/default",
        "search_url": "https://techtransfer.universityofcalifornia.edu/default",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies for licensing from the University of California",
        "notes": "Institution-native public UC system available technologies catalog override.",
    },
    "universityofflorida": {
        "institution_name": "University of Florida",
        "host": "ufinnovate.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://ufinnovate.technologypublisher.com/",
        "search_url": "https://ufinnovate.technologypublisher.com/site/search",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Available Technologies | UF Innovate",
        "notes": "Institution-native public available technologies catalog override for University of Florida.",
    },
    "universityofhawaii": {
        "institution_name": "University of Hawaii",
        "host": "universityofhawaii.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://universityofhawaii.technologypublisher.com/",
        "search_url": "https://universityofhawaii.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Office of Technology Transfer Technology Search | University of Hawaii",
        "notes": "Institution-native public University of Hawaii technology catalog managed by the Office of Innovation and Commercialization.",
    },
    "universityofsouthflorida": {
        "institution_name": "University of South Florida",
        "host": "usf.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://usf.technologypublisher.com/",
        "search_url": "https://usf.technologypublisher.com/site/search",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Available Technologies | USF Research & Innovation",
        "notes": "Institution-native public available technologies catalog override for University of South Florida.",
    },
    "theresearchfoundationforthestateuniversityofnewyork": {
        "institution_name": "The Research Foundation for The State University of New York",
        "host": "suny.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://suny.technologypublisher.com/",
        "search_url": "https://suny.technologypublisher.com/site/search",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Welcome to SUNY TechConnect",
        "notes": "System-level SUNY TechConnect public catalog override for the SUNY Research Foundation respondent.",
    },
    "theuabresearchfoundation": {
        "institution_name": "The UAB Research Foundation",
        "host": "uab.flintbox.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://uab.flintbox.com/",
        "search_url": "https://uab.flintbox.com/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies | UAB",
        "notes": "Institution-native public UAB technology catalog via Flintbox.",
    },
    "universityofsoutherncalifornia": {
        "institution_name": "University of Southern California",
        "host": "usc.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://usc.technologypublisher.com/",
        "search_url": "https://usc.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "USC-developed technologies for partnership and licensing",
        "notes": "Institution-native public USC Stevens Center innovation database via Technology Publisher.",
    },
    "icahnschoolofmedicineatmountsinai": {
        "institution_name": "Icahn School of Medicine at Mount Sinai",
        "host": "ip.mountsinai.org",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://ip.mountsinai.org/technologies/",
        "search_url": "https://ip.mountsinai.org/technologies/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Mount Sinai Technologies",
        "notes": "Institution-native public Mount Sinai Innovation Partners technologies catalog.",
    },
    "bostonchildrenshospital": {
        "institution_name": "Boston Children's Hospital",
        "host": "bch.technologypublisher.com",
        "source_type": "technologypublisher",
        "catalog_family": "Technology Publisher",
        "access_status": "verified-direct",
        "preferred_url": "https://bch.technologypublisher.com/",
        "search_url": "https://bch.technologypublisher.com/advancedsearch.aspx",
        "parser_strategy": "technologypublisher_search",
        "title_hint": "Search Technologies | Boston Children's Hospital",
        "notes": "Institution-native public Boston Children's Hospital technology catalog linked from TIDO Tech Search.",
    },
    "universityofiowaresearchfoundation": {
        "institution_name": "University of Iowa Research Foundation",
        "host": "uiowa.flintbox.com",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://uiowa.flintbox.com/categories",
        "search_url": "https://uiowa.flintbox.com/categories",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "Available Technologies | University of Iowa Research Foundation",
        "notes": "Institution-native public University of Iowa technology catalog via Flintbox.",
    },
    "universityoftexasatelpaso": {
        "institution_name": "University of Texas at El Paso",
        "host": "utep.tradespacemarket.com",
        "source_type": "tradespace_market",
        "catalog_family": "TradeSpace Market",
        "access_status": "verified-direct",
        "preferred_url": "https://utep.tradespacemarket.com/",
        "search_url": "https://utep.tradespacemarket.com/",
        "parser_strategy": "tradespace_market_catalog",
        "title_hint": "Explore Innovative Technologies | University of Texas at El Paso",
        "notes": "Institution-native public UTEP technology marketplace hosted on TradeSpace.",
    },
    "universityofwisconsinmadisonwisconsinalumniresearchfoundation": {
        "institution_name": "University of Wisconsin-Madison/Wisconsin Alumni Research Foundation",
        "host": "www.warf.org",
        "source_type": "custom_catalog",
        "catalog_family": "Custom University Catalogs",
        "access_status": "verified-direct",
        "preferred_url": "https://www.warf.org/commercialize/technologies/",
        "search_url": "https://www.warf.org/commercialize/technologies/",
        "parser_strategy": "custom_html_or_feed",
        "title_hint": "WARF Technologies",
        "notes": "Institution-native public WARF technology portfolio for UW-Madison inventions.",
    },
}


def _default_search_url(host: str) -> str:
    if host == "www.technologypublisher.com":
        return ""
    return f"https://{host}/site/search"


def _default_parser_strategy(host: str) -> str:
    if host == "www.technologypublisher.com":
        return "marketing_root"
    return "technologypublisher_search"


def _merge_notes(base_notes: str, suffix: str) -> str:
    if not suffix:
        return base_notes
    if not base_notes:
        return suffix
    return f"{base_notes}; {suffix}"


def _normalize_name(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _build_override_entry(override: dict[str, str]) -> SourceRegistryEntry:
    return SourceRegistryEntry(
        institution_name=override["institution_name"],
        host=override["host"],
        source_type=override["source_type"],
        status="observed",
        catalog_family=override["catalog_family"],
        access_status=override["access_status"],
        preferred_url=override["preferred_url"],
        search_url=override["search_url"],
        rss_url="",
        parser_strategy=override["parser_strategy"],
        title_hint=override["title_hint"],
        notes=override["notes"],
    )


def technology_publisher_host_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with TECHNOLOGY_PUBLISHER_REGISTRY.open("r", encoding="utf-8", newline="") as handle:
        reader = DictReader(handle)
        for row in reader:
            host = row["host"].strip().lower()
            institution_name = row["institution_name"].strip()
            if host and institution_name:
                mapping[host] = institution_name
    return mapping


def load_autm_2022_institutions() -> list[str]:
    with AUTM_2022_INSTITUTIONS.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def load_autm_2018_institutions() -> list[str]:
    with AUTM_2018_INSTITUTIONS.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def load_autm_combined_deduped_institutions() -> list[str]:
    combined = load_autm_2018_institutions() + load_autm_2022_institutions()
    deduped_by_name: dict[str, str] = {}
    for institution_name in combined:
        deduped_by_name.setdefault(_normalize_name(institution_name), institution_name)
    return sorted(deduped_by_name.values())


def load_campus_family_registry() -> CampusFamilyRegistrySummary:
    entries: list[CampusFamilyRegistryEntry] = []
    with CAMPUS_FAMILY_REGISTRY.open("r", encoding="utf-8", newline="") as handle:
        reader = DictReader(handle)
        for row in reader:
            entries.append(
                CampusFamilyRegistryEntry(
                    family_key=row["family_key"].strip(),
                    family_name=row["family_name"].strip(),
                    member_institution_name=row["member_institution_name"].strip(),
                    member_role=row["member_role"].strip(),
                    source_type=row.get("source_type", "").strip(),
                    preferred_url=row.get("preferred_url", "").strip(),
                    search_url=row.get("search_url", "").strip(),
                    coverage_status=row.get("coverage_status", "").strip(),
                    notes=row.get("notes", "").strip(),
                )
            )

    return CampusFamilyRegistrySummary(
        registry_name="Campus Family Registry",
        family_count=len({entry.family_key for entry in entries}),
        entries=entries,
    )


def _family_key_lookup() -> tuple[dict[str, str], dict[str, str]]:
    member_to_family_key: dict[str, str] = {}
    family_name_by_key: dict[str, str] = {}
    for entry in load_campus_family_registry().entries:
        family_name_by_key[entry.family_key] = entry.family_name
        member_to_family_key[_normalize_name(entry.member_institution_name)] = entry.family_key
    return member_to_family_key, family_name_by_key


def _verified_direct_registry_lookup() -> dict[str, SourceRegistryEntry]:
    lookup: dict[str, SourceRegistryEntry] = {}
    for normalized_name, override in _PUBLIC_CATALOG_OVERRIDES.items():
        lookup[normalized_name] = _build_override_entry(override)
    for entry in load_technology_publisher_registry().entries:
        if entry.access_status != "verified-direct":
            continue
        normalized_name = _normalize_name(entry.institution_name)
        lookup.setdefault(normalized_name, entry)
    return lookup


def _build_autm_coverage_summary(institutions: list[str], coverage_name: str) -> InstitutionCoverageSummary:
    direct_lookup = _verified_direct_registry_lookup()
    entries: list[InstitutionCoverageEntry] = []

    for institution_name in institutions:
        candidate_names = [institution_name, *_AUTM_DIRECT_SOURCE_ALIASES.get(institution_name, [])]
        matched_entry: SourceRegistryEntry | None = None
        matched_candidate = ""

        for candidate_name in candidate_names:
            matched_entry = direct_lookup.get(_normalize_name(candidate_name))
            if matched_entry:
                matched_candidate = candidate_name
                break

        if matched_entry:
            notes: list[str] = []
            if matched_candidate != institution_name:
                notes.append(f"Matched via alias '{matched_candidate}'.")
            entries.append(
                InstitutionCoverageEntry(
                    institution_name=institution_name,
                    coverage_status="direct-covered",
                    matched_source_family=matched_entry.catalog_family,
                    matched_source_type=matched_entry.source_type,
                    matched_registry_institution=matched_entry.institution_name,
                    preferred_url=matched_entry.preferred_url,
                    notes=notes,
                )
            )
            continue

        entries.append(
            InstitutionCoverageEntry(
                institution_name=institution_name,
                coverage_status="missing-direct",
                notes=["No verified institution-native source is currently registered."],
            )
        )

    direct_coverage_count = sum(1 for entry in entries if entry.coverage_status == "direct-covered")
    target_institution_count = len(entries)
    return InstitutionCoverageSummary(
        coverage_name=coverage_name,
        target_institution_count=target_institution_count,
        direct_coverage_count=direct_coverage_count,
        missing_direct_count=target_institution_count - direct_coverage_count,
        canberra_retired=direct_coverage_count == target_institution_count,
        entries=entries,
    )


def load_autm_2018_coverage_summary() -> InstitutionCoverageSummary:
    return _build_autm_coverage_summary(
        institutions=load_autm_2018_institutions(),
        coverage_name="AUTM 2018 US Licensing Activity Survey Respondents",
    )


def load_autm_2022_coverage_summary() -> InstitutionCoverageSummary:
    return _build_autm_coverage_summary(
        institutions=load_autm_2022_institutions(),
        coverage_name="AUTM 2022 US Licensing Activity Survey Respondents",
    )


def load_autm_combined_coverage_summary() -> InstitutionCoverageSummary:
    return _build_autm_coverage_summary(
        institutions=load_autm_combined_deduped_institutions(),
        coverage_name="AUTM Combined Deduped Respondents",
    )


def load_autm_combined_family_coverage_summary() -> OrganizationFamilyCoverageSummary:
    respondent_summary = load_autm_combined_coverage_summary()
    member_to_family_key, family_name_by_key = _family_key_lookup()
    grouped_entries: dict[str, list[InstitutionCoverageEntry]] = {}
    family_display_names: dict[str, str] = {}

    for entry in respondent_summary.entries:
        normalized_name = _normalize_name(entry.institution_name)
        family_key = member_to_family_key.get(normalized_name, normalized_name)
        family_name = family_name_by_key.get(family_key, entry.institution_name)
        family_display_names[family_key] = family_name
        grouped_entries.setdefault(family_key, []).append(entry)

    summary_entries: list[OrganizationFamilyCoverageEntry] = []
    for family_key, grouped in sorted(grouped_entries.items(), key=lambda item: family_display_names[item[0]]):
        covered = [entry for entry in grouped if entry.coverage_status == "direct-covered"]
        preferred_urls = sorted({entry.preferred_url for entry in covered if entry.preferred_url})
        represented_institutions = sorted(entry.institution_name for entry in grouped)
        covered_institutions = sorted(entry.institution_name for entry in covered)
        notes: list[str] = []
        if len(grouped) > 1:
            notes.append("Family-level coverage collapses related system and campus respondents.")
        summary_entries.append(
            OrganizationFamilyCoverageEntry(
                family_key=family_key,
                family_name=family_display_names[family_key],
                coverage_status="direct-covered" if covered else "missing-direct",
                target_member_count=len(grouped),
                covered_member_count=len(covered),
                represented_institutions=represented_institutions,
                covered_institutions=covered_institutions,
                preferred_urls=preferred_urls,
                notes=notes,
            )
        )

    covered_family_count = sum(1 for entry in summary_entries if entry.coverage_status == "direct-covered")
    target_family_count = len(summary_entries)
    return OrganizationFamilyCoverageSummary(
        coverage_name="AUTM Combined System-Aware Family Coverage",
        target_family_count=target_family_count,
        covered_family_count=covered_family_count,
        missing_family_count=target_family_count - covered_family_count,
        entries=summary_entries,
    )


def resolve_preferred_catalog(
    institution_name: str,
    aggregate_source_url: str | None = None,
    aggregate_source_type: str = "aggregate",
) -> tuple[SourceRegistryEntry | None, str, str, list[str]]:
    direct_lookup = _verified_direct_registry_lookup()
    direct_entry = direct_lookup.get(_normalize_name(institution_name))
    if direct_entry:
        selected_url = direct_entry.preferred_url or direct_entry.search_url or direct_entry.rss_url
        notes = [
            "Institution-native catalog preferred when directly reachable.",
        ]
        if direct_entry.source_type != "technologypublisher":
            notes.append("Using institution-native public catalog override instead of Technology Publisher host.")
        if aggregate_source_url:
            notes.append("Aggregate source retained only as fallback.")
        return direct_entry, selected_url, direct_entry.source_type, notes

    notes = ["No institution-native catalog found in the current direct registry."]
    if aggregate_source_url:
        notes.append("Falling back to aggregate source because no direct catalog is registered.")
        return None, aggregate_source_url, aggregate_source_type, notes
    return None, "", "", notes


def load_technology_publisher_registry() -> SourceRegistrySummary:
    entries: list[SourceRegistryEntry] = []
    with TECHNOLOGY_PUBLISHER_REGISTRY.open("r", encoding="utf-8", newline="") as handle:
        reader = DictReader(handle)
        for row in reader:
            host = row["host"]
            probe_status = _TECHNOLOGY_PUBLISHER_PROBE_STATUS.get(host, {})
            search_url = _default_search_url(host)
            preferred_url = probe_status.get("preferred_url", search_url)
            entries.append(
                SourceRegistryEntry(
                    institution_name=row["institution_name"],
                    host=host,
                    source_type=row["source_type"],
                    status=row["status"],
                    catalog_family="Technology Publisher",
                    access_status=probe_status.get("access_status", "observed"),
                    preferred_url=preferred_url,
                    search_url=search_url,
                    rss_url=row.get("rss_url", ""),
                    parser_strategy=row.get("parser_strategy") or _default_parser_strategy(host),
                    title_hint=row.get("title_hint", ""),
                    notes=_merge_notes(row.get("notes", ""), probe_status.get("notes_suffix", "")),
                )
            )

    return SourceRegistrySummary(
        registry_name="Technology Publisher",
        observed_host_count=len(entries),
        rough_active_count_low=35,
        rough_active_count_high=45,
        entries=entries,
    )


def load_catalog_family_registry() -> SourceCatalogFamilySummary:
    autm_coverage = load_autm_2022_coverage_summary()
    families = [
        SourceCatalogFamilyEntry(
                family_name="Technology Publisher",
                source_type="technologypublisher",
                priority=1,
                coverage_status="verified-starter-inventory",
                parser_strategy="technologypublisher_search",
                example_urls=[
                    "https://uchicago.technologypublisher.com/site/search",
                    "https://ucla.technologypublisher.com/site/search",
                    "https://upenn.technologypublisher.com/site/search",
                ],
                detection_patterns=[
                    "*.technologypublisher.com/site/search",
                    "*.technologypublisher.com/tech/*",
                    "technologypublisher host assets embedded in feed items",
                ],
                notes="Institution-native Technology Publisher catalogs should be preferred over Canberra-style aggregates when available.",
        ),
        SourceCatalogFamilyEntry(
                family_name="Wellspring Sophia",
                source_type="wellspring_sophia",
                priority=2,
                coverage_status="initial-baseline",
                parser_strategy="wellspring_catalog",
                example_urls=[
                    "https://swcatalog.umd.edu/well-spring-sophia",
                    "https://www.wellspring.com/sophia",
                ],
                detection_patterns=[
                    "institution-hosted pages naming Well Spring Sophia or Wellspring Sophia",
                    "catalog pages exposing searchable technology listings outside technologypublisher.com",
                ],
                notes="Initial baseline confirmed from University of Maryland software catalog and the Wellspring Sophia product page; host-by-host commercialization catalog inventory is still pending.",
        ),
        SourceCatalogFamilyEntry(
                family_name="Custom University Catalogs",
                source_type="custom_catalog",
                priority=3,
                coverage_status="framework-only",
                parser_strategy="custom_html_or_feed",
                example_urls=[],
                detection_patterns=[
                    "direct institutional tech transfer catalog domains",
                    "custom search pages and institution-specific RSS or sitemap feeds",
                ],
                notes="Used for institutions running their own catalog stack instead of Technology Publisher or Wellspring.",
        ),
        SourceCatalogFamilyEntry(
                family_name="TradeSpace Market",
                source_type="tradespace_market",
                priority=4,
                coverage_status="identified-direct",
                parser_strategy="tradespace_market_catalog",
                example_urls=[
                    "https://utep.tradespacemarket.com/",
                    "https://umventures.tradespacemarket.com/",
                ],
                detection_patterns=[
                    "*.tradespacemarket.com/opportunities/*",
                    "tradespace market opportunity listings with availability terms",
                ],
                notes="Used for institution-native TradeSpace commercialization marketplaces exposing public technology opportunities.",
        ),
    ]

    if not autm_coverage.canberra_retired:
        families.append(
            SourceCatalogFamilyEntry(
                family_name="Canberra Aggregate",
                source_type="inteum_rss",
                priority=5,
                coverage_status="supported-gap-fill",
                parser_strategy="inteum_rss",
                example_urls=[
                    "https://www.canberra-ip.com",
                ],
                detection_patterns=[
                    "rss feeds with dataField namespace",
                    "aggregated items containing technologypublisher asset hosts or institution emails",
                ],
                notes=(
                    "Useful only as gap-fill while direct institutional coverage is incomplete. "
                    f"Current AUTM 2022 direct coverage: {autm_coverage.direct_coverage_count}/"
                    f"{autm_coverage.target_institution_count}. Remove Canberra once direct coverage reaches 100%."
                ),
            )
        )

    return SourceCatalogFamilySummary(
        registry_name="Commercialization Catalog Families",
        families=families,
    )