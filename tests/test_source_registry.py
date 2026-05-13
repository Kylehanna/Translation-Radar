import unittest

from translation_radar_api.models import PreferredCatalogRequest
from translation_radar_api.routes.sources import build_preferred_catalog_response
from translation_radar_api.sources.registry import (
    load_autm_combined_coverage_summary,
    load_autm_combined_family_coverage_summary,
    load_autm_2018_coverage_summary,
    load_autm_2022_coverage_summary,
    load_campus_family_registry,
    load_catalog_family_registry,
    load_technology_publisher_registry,
)


class SourceRegistryTests(unittest.TestCase):
    def test_loads_technology_publisher_registry(self) -> None:
        summary = load_technology_publisher_registry()

        self.assertEqual(summary.registry_name, "Technology Publisher")
        self.assertEqual(summary.observed_host_count, 42)
        hosts = {entry.host for entry in summary.entries}
        self.assertIn("utrf.technologypublisher.com", hosts)
        self.assertIn("broadinstitute.technologypublisher.com", hosts)
        self.assertIn("uchicago.technologypublisher.com", hosts)
        upenn_entry = next(entry for entry in summary.entries if entry.host == "upenn.technologypublisher.com")
        self.assertEqual(upenn_entry.search_url, "https://upenn.technologypublisher.com/site/search")
        self.assertEqual(upenn_entry.parser_strategy, "technologypublisher_search")
        self.assertEqual(upenn_entry.access_status, "verified-direct")
        self.assertEqual(upenn_entry.preferred_url, "https://upenn.technologypublisher.com/site/search")

        uchicago_entry = next(entry for entry in summary.entries if entry.host == "uchicago.technologypublisher.com")
        self.assertEqual(uchicago_entry.institution_name, "University of Chicago")
        self.assertEqual(uchicago_entry.preferred_url, "https://uchicago.technologypublisher.com/site/search")

    def test_loads_catalog_family_registry(self) -> None:
        summary = load_catalog_family_registry()

        family_names = {entry.family_name for entry in summary.families}
        self.assertIn("Technology Publisher", family_names)
        self.assertIn("Wellspring Sophia", family_names)
        self.assertIn("TradeSpace Market", family_names)
        self.assertIn("Custom University Catalogs", family_names)
        self.assertIn("Canberra Aggregate", family_names)

        wellspring_entry = next(entry for entry in summary.families if entry.family_name == "Wellspring Sophia")
        self.assertEqual(wellspring_entry.coverage_status, "initial-baseline")
        self.assertIn("https://swcatalog.umd.edu/well-spring-sophia", wellspring_entry.example_urls)

        canberra_entry = next(entry for entry in summary.families if entry.family_name == "Canberra Aggregate")
        self.assertEqual(canberra_entry.coverage_status, "supported-gap-fill")
        self.assertIn("Current AUTM 2022 direct coverage:", canberra_entry.notes)

    def test_loads_campus_family_registry(self) -> None:
        summary = load_campus_family_registry()

        self.assertEqual(summary.registry_name, "Campus Family Registry")
        self.assertGreaterEqual(summary.family_count, 7)

        uc_entries = [entry for entry in summary.entries if entry.family_key == "university_of_california"]
        self.assertEqual(len(uc_entries), 10)

        ut_dallas_entry = next(
            entry for entry in summary.entries if entry.member_institution_name == "University of Texas at Dallas"
        )
        self.assertEqual(ut_dallas_entry.preferred_url, "https://utdallas.technologypublisher.com/site/search")

        umass_lowell_entry = next(
            entry for entry in summary.entries if entry.member_institution_name == "University of Massachusetts Lowell"
        )
        self.assertEqual(umass_lowell_entry.preferred_url, "https://www.uml.edu/Research/OTC/technologies/")

    def test_loads_autm_2022_coverage_summary(self) -> None:
        summary = load_autm_2022_coverage_summary()

        self.assertGreater(summary.target_institution_count, 100)
        self.assertEqual(summary.direct_coverage_count, 58)
        self.assertFalse(summary.canberra_retired)

        upenn_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Pennsylvania")
        self.assertEqual(upenn_entry.coverage_status, "direct-covered")
        self.assertEqual(upenn_entry.preferred_url, "https://upenn.technologypublisher.com/site/search")

        uchicago_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Chicago")
        self.assertEqual(uchicago_entry.coverage_status, "direct-covered")
        self.assertEqual(uchicago_entry.preferred_url, "https://uchicago.technologypublisher.com/site/search")

        harvard_entry = next(entry for entry in summary.entries if entry.institution_name == "Harvard University")
        self.assertEqual(harvard_entry.coverage_status, "direct-covered")
        self.assertEqual(
            harvard_entry.preferred_url,
            "https://otd.harvard.edu/industry-investors/commercialization-opportunities/",
        )

        jhuapl_entry = next(
            entry for entry in summary.entries if entry.institution_name == "Johns Hopkins University Applied Physics Laboratory"
        )
        self.assertEqual(jhuapl_entry.coverage_status, "direct-covered")
        self.assertEqual(jhuapl_entry.preferred_url, "https://www.jhuapl.edu/tech-transfer/technologies-patents")

        mit_entry = next(entry for entry in summary.entries if entry.institution_name == "Massachusetts Institute of Technology")
        self.assertEqual(mit_entry.coverage_status, "direct-covered")
        self.assertEqual(mit_entry.preferred_url, "https://tlo.mit.edu/industry-entrepreneurs/available-technologies")

        northwestern_entry = next(entry for entry in summary.entries if entry.institution_name == "Northwestern University")
        self.assertEqual(northwestern_entry.coverage_status, "direct-covered")
        self.assertEqual(northwestern_entry.preferred_url, "https://inventions.invo.northwestern.edu/")

        ucla_entry = next(entry for entry in summary.entries if entry.institution_name == "University of California, Los Angeles")
        self.assertEqual(ucla_entry.coverage_status, "direct-covered")
        self.assertEqual(ucla_entry.preferred_url, "https://techtransfer.universityofcalifornia.edu/default?campus=LA")

        uf_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Florida")
        self.assertEqual(uf_entry.coverage_status, "direct-covered")
        self.assertEqual(uf_entry.preferred_url, "https://ufinnovate.technologypublisher.com/")

        usf_entry = next(entry for entry in summary.entries if entry.institution_name == "University of South Florida")
        self.assertEqual(usf_entry.coverage_status, "direct-covered")
        self.assertEqual(usf_entry.preferred_url, "https://usf.technologypublisher.com/")

        suny_entry = next(
            entry for entry in summary.entries if entry.institution_name == "The Research Foundation for The State University of New York"
        )
        self.assertEqual(suny_entry.coverage_status, "direct-covered")
        self.assertEqual(suny_entry.preferred_url, "https://suny.technologypublisher.com/")

        uc_expected_urls = {
            "University of California, Berkeley": "https://techtransfer.universityofcalifornia.edu/default?campus=BK",
            "University of California, Irvine": "https://techtransfer.universityofcalifornia.edu/default?campus=IR",
            "University of California, Merced": "https://techtransfer.universityofcalifornia.edu/default?campus=MC",
            "University of California, Riverside": "https://techtransfer.universityofcalifornia.edu/default?campus=RV",
            "University of California, San Diego": "https://techtransfer.universityofcalifornia.edu/default?campus=SD",
            "University of California, San Francisco": "https://techtransfer.universityofcalifornia.edu/default?campus=SF",
            "University of California, Santa Barbara": "https://techtransfer.universityofcalifornia.edu/default?campus=SB",
            "University of California, Santa Cruz": "https://techtransfer.universityofcalifornia.edu/default?campus=SC",
        }
        for institution_name, expected_url in uc_expected_urls.items():
            entry = next(entry for entry in summary.entries if entry.institution_name == institution_name)
            self.assertEqual(entry.coverage_status, "direct-covered")
            self.assertEqual(entry.preferred_url, expected_url)

        expected_new_2022_urls = {
            "Arizona State University": "https://skysong.technologypublisher.com/",
            "Boston Children's Hospital": "https://bch.technologypublisher.com/",
            "Boston University": "https://bu.flintbox.com/",
            "Brown University": "https://brown.technologypublisher.com/",
            "Case Western Reserve University": "https://case.portals.in-part.com/",
            "Cedars-Sinai Medical Center": "https://cedars.flintbox.com/",
            "Cincinnati Children's Hospital Medical Center": "https://www.cincinnatichildrens.org/research/support/innovation-ventures/",
            "Carnegie Mellon University": "http://cmu.flintbox.com/",
            "Columbia University": "https://inventions.techventures.columbia.edu/categories",
            "Cornell University": "https://cornell.flintbox.com/",
            "Dana-Farber Cancer Institute": "https://innovations.dana-farber.org/",
            "Fred Hutchinson Cancer Center": "https://www.fredhutch.org/en/investors/business-development/available-technologies.html",
            "Georgia Institute of Technology": "https://licensing.research.gatech.edu/technologies",
            "Icahn School of Medicine at Mount Sinai": "https://ip.mountsinai.org/technologies/",
            "Jackson State University": "https://www.jsums.edu/technologytransfer/industry/",
            "Michigan State University": "https://msut.technologypublisher.com/",
            "New York University": "https://license.tov.med.nyu.edu/",
            "North Carolina A&T State University": "https://ncat.edu/research/technology-transfer/available-technologies.php",
            "North Carolina State University": "https://ncsu.portals.in-part.com/",
            "Purdue Research Foundation": "https://licensing.prf.org/",
            "Stanford University": "https://techfinder.stanford.edu/",
            "The Salk Institute for Biological Studies": "https://salk.portals.in-part.com/",
            "University of Cincinnati": "https://uc.technologypublisher.com/",
            "University of Hawaii": "https://universityofhawaii.technologypublisher.com/",
            "University of Iowa Research Foundation": "https://uiowa.flintbox.com/categories",
            "University of Southern California": "https://usc.technologypublisher.com/",
            "University of Texas at El Paso": "https://utep.tradespacemarket.com/",
            "University of Wisconsin-Madison/Wisconsin Alumni Research Foundation": "https://www.warf.org/commercialize/technologies/",
        }
        for institution_name, expected_url in expected_new_2022_urls.items():
            entry = next(entry for entry in summary.entries if entry.institution_name == institution_name)
            self.assertEqual(entry.coverage_status, "direct-covered")
            self.assertEqual(entry.preferred_url, expected_url)

    def test_loads_autm_2018_coverage_summary(self) -> None:
        summary = load_autm_2018_coverage_summary()

        self.assertEqual(summary.target_institution_count, 188)
        self.assertEqual(summary.direct_coverage_count, 48)
        self.assertFalse(summary.canberra_retired)

        upenn_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Pennsylvania")
        self.assertEqual(upenn_entry.coverage_status, "direct-covered")
        self.assertEqual(upenn_entry.preferred_url, "https://upenn.technologypublisher.com/site/search")

        uchicago_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Chicago")
        self.assertEqual(uchicago_entry.coverage_status, "direct-covered")
        self.assertEqual(uchicago_entry.preferred_url, "https://uchicago.technologypublisher.com/site/search")

        mit_entry = next(entry for entry in summary.entries if entry.institution_name == "Massachusetts Institute of Technology")
        self.assertEqual(mit_entry.coverage_status, "direct-covered")
        self.assertEqual(mit_entry.preferred_url, "https://tlo.mit.edu/industry-entrepreneurs/available-technologies")

        northwestern_entry = next(entry for entry in summary.entries if entry.institution_name == "Northwestern University")
        self.assertEqual(northwestern_entry.coverage_status, "direct-covered")
        self.assertEqual(northwestern_entry.preferred_url, "https://inventions.invo.northwestern.edu/")

        uf_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Florida")
        self.assertEqual(uf_entry.coverage_status, "direct-covered")
        self.assertEqual(uf_entry.preferred_url, "https://ufinnovate.technologypublisher.com/")

        uc_system_entry = next(entry for entry in summary.entries if entry.institution_name == "University of California System")
        self.assertEqual(uc_system_entry.coverage_status, "direct-covered")
        self.assertEqual(uc_system_entry.preferred_url, "https://techtransfer.universityofcalifornia.edu/default")

        suny_entry = next(
            entry for entry in summary.entries if entry.institution_name == "The Research Foundation for The State University of New York"
        )
        self.assertEqual(suny_entry.coverage_status, "direct-covered")
        self.assertEqual(suny_entry.preferred_url, "https://suny.technologypublisher.com/")

        expected_new_2018_urls = {
            "Arizona State University": "https://skysong.technologypublisher.com/",
            "Brown University": "https://brown.technologypublisher.com/",
            "Case Western Reserve University": "https://case.portals.in-part.com/",
            "Cedars-Sinai Medical Center": "https://cedars.flintbox.com/",
            "Carnegie Mellon University": "http://cmu.flintbox.com/",
            "Children's Hospital Boston": "https://bch.technologypublisher.com/",
            "Columbia University": "https://inventions.techventures.columbia.edu/categories",
            "Cornell University": "https://cornell.flintbox.com/",
            "Dana-Farber Cancer Institute": "https://innovations.dana-farber.org/",
            "Georgia Institute of Technology": "https://licensing.research.gatech.edu/technologies",
            "H. Lee Moffitt Cancer Center & Research Institute": "https://moffitt.technologypublisher.com/",
            "Michigan State University": "https://msut.technologypublisher.com/",
            "New York University": "https://license.tov.med.nyu.edu/",
            "North Carolina State University": "https://ncsu.portals.in-part.com/",
            "Purdue Research Foundation": "https://licensing.prf.org/",
            "Stanford University": "https://techfinder.stanford.edu/",
            "The Salk Institute for Biological Studies": "https://salk.portals.in-part.com/",
            "The UAB Research Foundation": "https://uab.flintbox.com/",
            "University of Cincinnati": "https://uc.technologypublisher.com/",
            "University of Hawaii": "https://universityofhawaii.technologypublisher.com/",
            "University of Iowa Research Foundation": "https://uiowa.flintbox.com/categories",
            "University of Southern California": "https://usc.technologypublisher.com/",
            "University of Wisconsin-Madison/Wisconsin Alumni Research Foundation": "https://www.warf.org/commercialize/technologies/",
        }
        for institution_name, expected_url in expected_new_2018_urls.items():
            entry = next(entry for entry in summary.entries if entry.institution_name == institution_name)
            self.assertEqual(entry.coverage_status, "direct-covered")
            self.assertEqual(entry.preferred_url, expected_url)

    def test_loads_autm_combined_coverage_summary(self) -> None:
        summary = load_autm_combined_coverage_summary()

        self.assertEqual(summary.target_institution_count, 237)
        self.assertEqual(summary.direct_coverage_count, 65)

        uab_entry = next(entry for entry in summary.entries if entry.institution_name == "The UAB Research Foundation")
        self.assertEqual(uab_entry.coverage_status, "direct-covered")
        self.assertEqual(uab_entry.preferred_url, "https://uab.flintbox.com/")

        hawaii_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Hawaii")
        self.assertEqual(hawaii_entry.coverage_status, "direct-covered")
        self.assertEqual(hawaii_entry.preferred_url, "https://universityofhawaii.technologypublisher.com/")

        cincinnati_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Cincinnati")
        self.assertEqual(cincinnati_entry.coverage_status, "direct-covered")
        self.assertEqual(cincinnati_entry.preferred_url, "https://uc.technologypublisher.com/")

        mount_sinai_entry = next(
            entry for entry in summary.entries if entry.institution_name == "Icahn School of Medicine at Mount Sinai"
        )
        self.assertEqual(mount_sinai_entry.coverage_status, "direct-covered")
        self.assertEqual(mount_sinai_entry.preferred_url, "https://ip.mountsinai.org/technologies/")

        boston_childrens_entry = next(entry for entry in summary.entries if entry.institution_name == "Boston Children's Hospital")
        self.assertEqual(boston_childrens_entry.coverage_status, "direct-covered")
        self.assertEqual(boston_childrens_entry.preferred_url, "https://bch.technologypublisher.com/")

        childrens_boston_entry = next(entry for entry in summary.entries if entry.institution_name == "Children's Hospital Boston")
        self.assertEqual(childrens_boston_entry.coverage_status, "direct-covered")
        self.assertEqual(childrens_boston_entry.preferred_url, "https://bch.technologypublisher.com/")

        cincinnati_childrens_entry = next(
            entry for entry in summary.entries if entry.institution_name == "Cincinnati Children's Hospital Medical Center"
        )
        self.assertEqual(cincinnati_childrens_entry.coverage_status, "direct-covered")
        self.assertEqual(
            cincinnati_childrens_entry.preferred_url,
            "https://www.cincinnatichildrens.org/research/support/innovation-ventures/",
        )

        cedars_entry = next(entry for entry in summary.entries if entry.institution_name == "Cedars-Sinai Medical Center")
        self.assertEqual(cedars_entry.coverage_status, "direct-covered")
        self.assertEqual(cedars_entry.preferred_url, "https://cedars.flintbox.com/")

        dana_farber_entry = next(entry for entry in summary.entries if entry.institution_name == "Dana-Farber Cancer Institute")
        self.assertEqual(dana_farber_entry.coverage_status, "direct-covered")
        self.assertEqual(dana_farber_entry.preferred_url, "https://innovations.dana-farber.org/")

        fred_hutch_entry = next(entry for entry in summary.entries if entry.institution_name == "Fred Hutchinson Cancer Center")
        self.assertEqual(fred_hutch_entry.coverage_status, "direct-covered")
        self.assertEqual(
            fred_hutch_entry.preferred_url,
            "https://www.fredhutch.org/en/investors/business-development/available-technologies.html",
        )

        usc_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Southern California")
        self.assertEqual(usc_entry.coverage_status, "direct-covered")
        self.assertEqual(usc_entry.preferred_url, "https://usc.technologypublisher.com/")

        utep_entry = next(entry for entry in summary.entries if entry.institution_name == "University of Texas at El Paso")
        self.assertEqual(utep_entry.coverage_status, "direct-covered")
        self.assertEqual(utep_entry.preferred_url, "https://utep.tradespacemarket.com/")

        moffitt_entry = next(
            entry for entry in summary.entries if entry.institution_name == "H. Lee Moffitt Cancer Center & Research Institute"
        )
        self.assertEqual(moffitt_entry.coverage_status, "direct-covered")
        self.assertEqual(moffitt_entry.preferred_url, "https://moffitt.technologypublisher.com/")

        cmu_entry = next(entry for entry in summary.entries if entry.institution_name == "Carnegie Mellon University")
        self.assertEqual(cmu_entry.coverage_status, "direct-covered")
        self.assertEqual(cmu_entry.preferred_url, "http://cmu.flintbox.com/")

        cornell_entry = next(entry for entry in summary.entries if entry.institution_name == "Cornell University")
        self.assertEqual(cornell_entry.coverage_status, "direct-covered")
        self.assertEqual(cornell_entry.preferred_url, "https://cornell.flintbox.com/")

        ncat_entry = next(entry for entry in summary.entries if entry.institution_name == "North Carolina A&T State University")
        self.assertEqual(ncat_entry.coverage_status, "direct-covered")
        self.assertEqual(ncat_entry.preferred_url, "https://ncat.edu/research/technology-transfer/available-technologies.php")

        jsu_entry = next(entry for entry in summary.entries if entry.institution_name == "Jackson State University")
        self.assertEqual(jsu_entry.coverage_status, "direct-covered")
        self.assertEqual(jsu_entry.preferred_url, "https://www.jsums.edu/technologytransfer/industry/")

    def test_loads_autm_combined_family_coverage_summary(self) -> None:
        summary = load_autm_combined_family_coverage_summary()

        self.assertEqual(summary.coverage_name, "AUTM Combined System-Aware Family Coverage")
        self.assertEqual(summary.covered_family_count, 56)

        uc_family = next(entry for entry in summary.entries if entry.family_key == "university_of_california")
        self.assertEqual(uc_family.coverage_status, "direct-covered")
        self.assertEqual(uc_family.target_member_count, 10)
        self.assertEqual(uc_family.covered_member_count, 10)

        maryland_family = next(entry for entry in summary.entries if entry.family_key == "university_system_of_maryland")
        self.assertEqual(maryland_family.coverage_status, "missing-direct")
        self.assertEqual(maryland_family.target_member_count, 1)

        ut_family = next(entry for entry in summary.entries if entry.family_key == "university_of_texas")
        self.assertEqual(ut_family.coverage_status, "direct-covered")
        self.assertEqual(ut_family.covered_member_count, 1)

    def test_resolves_preferred_catalog_to_direct_institution_url(self) -> None:
        response = build_preferred_catalog_response(
            PreferredCatalogRequest(
                institution_name="University of Pennsylvania",
                aggregate_source_url="https://www.canberra-ip.com/rss",
                aggregate_source_type="inteum_rss",
            )
        )

        self.assertEqual(response.resolution_status, "direct-match")
        self.assertEqual(response.selected_url, "https://upenn.technologypublisher.com/site/search")
        self.assertEqual(response.selected_source_type, "technologypublisher")

    def test_prefers_public_catalog_override_for_jhu(self) -> None:
        response = build_preferred_catalog_response(
            PreferredCatalogRequest(
                institution_name="Johns Hopkins University",
                aggregate_source_url="https://www.canberra-ip.com/rss",
                aggregate_source_type="inteum_rss",
            )
        )

        self.assertEqual(response.resolution_status, "direct-match")
        self.assertEqual(response.selected_url, "https://ventures.jhu.edu/innovations/technologies/")
        self.assertEqual(response.selected_source_type, "custom_catalog")

    def test_resolves_harvard_to_public_catalog_override(self) -> None:
        response = build_preferred_catalog_response(
            PreferredCatalogRequest(
                institution_name="Harvard University",
                aggregate_source_url="https://www.canberra-ip.com/rss",
                aggregate_source_type="inteum_rss",
            )
        )

        self.assertEqual(response.resolution_status, "direct-match")
        self.assertEqual(
            response.selected_url,
            "https://otd.harvard.edu/industry-investors/commercialization-opportunities/",
        )
        self.assertEqual(response.selected_source_type, "custom_catalog")

    def test_resolves_jhuapl_to_public_catalog_override(self) -> None:
        response = build_preferred_catalog_response(
            PreferredCatalogRequest(
                institution_name="Johns Hopkins University Applied Physics Laboratory",
                aggregate_source_url="https://www.canberra-ip.com/rss",
                aggregate_source_type="inteum_rss",
            )
        )

        self.assertEqual(response.resolution_status, "direct-match")
        self.assertEqual(response.selected_url, "https://www.jhuapl.edu/tech-transfer/technologies-patents")
        self.assertEqual(response.selected_source_type, "custom_catalog")

    def test_resolves_shortlist_public_catalog_overrides(self) -> None:
        expected = {
            "Howard University": (
                "https://howard.portals.in-part.com/",
                "custom_catalog",
            ),
            "Jackson State University": (
                "https://www.jsums.edu/technologytransfer/industry/",
                "custom_catalog",
            ),
            "Massachusetts Institute of Technology": (
                "https://tlo.mit.edu/industry-entrepreneurs/available-technologies",
                "custom_catalog",
            ),
            "Boston University": (
                "https://bu.flintbox.com/",
                "custom_catalog",
            ),
            "Arizona State University": (
                "https://skysong.technologypublisher.com/",
                "technologypublisher",
            ),
            "Brown University": (
                "https://brown.technologypublisher.com/",
                "technologypublisher",
            ),
            "Case Western Reserve University": (
                "https://case.portals.in-part.com/",
                "custom_catalog",
            ),
            "Carnegie Mellon University": (
                "http://cmu.flintbox.com/",
                "custom_catalog",
            ),
            "North Carolina A&T State University": (
                "https://ncat.edu/research/technology-transfer/available-technologies.php",
                "custom_catalog",
            ),
            "Tuskegee University": (
                "https://www.tuskegee.edu/research-sponsored-programs/Technology-Transfer.html",
                "custom_catalog",
            ),
            "Columbia University": (
                "https://inventions.techventures.columbia.edu/categories",
                "custom_catalog",
            ),
            "Cornell University": (
                "https://cornell.flintbox.com/",
                "custom_catalog",
            ),
            "Georgia Institute of Technology": (
                "https://licensing.research.gatech.edu/technologies",
                "custom_catalog",
            ),
            "Purdue Research Foundation": (
                "https://licensing.prf.org/",
                "custom_catalog",
            ),
            "H. Lee Moffitt Cancer Center & Research Institute": (
                "https://moffitt.technologypublisher.com/",
                "technologypublisher",
            ),
            "Michigan State University": (
                "https://msut.technologypublisher.com/",
                "technologypublisher",
            ),
            "New York University": (
                "https://license.tov.med.nyu.edu/",
                "custom_catalog",
            ),
            "North Carolina State University": (
                "https://ncsu.portals.in-part.com/",
                "custom_catalog",
            ),
            "The UAB Research Foundation": (
                "https://uab.flintbox.com/",
                "custom_catalog",
            ),
            "Northwestern University": (
                "https://inventions.invo.northwestern.edu/",
                "custom_catalog",
            ),
            "Stanford University": (
                "https://techfinder.stanford.edu/",
                "custom_catalog",
            ),
            "The Salk Institute for Biological Studies": (
                "https://salk.portals.in-part.com/",
                "custom_catalog",
            ),
            "University of California, Los Angeles": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=LA",
                "custom_catalog",
            ),
            "University of Florida": (
                "https://ufinnovate.technologypublisher.com/",
                "technologypublisher",
            ),
            "University of South Florida": (
                "https://usf.technologypublisher.com/",
                "technologypublisher",
            ),
            "The Research Foundation for The State University of New York": (
                "https://suny.technologypublisher.com/",
                "technologypublisher",
            ),
            "University of Southern California": (
                "https://usc.technologypublisher.com/",
                "technologypublisher",
            ),
            "University of Texas at El Paso": (
                "https://utep.tradespacemarket.com/",
                "tradespace_market",
            ),
            "University of California, Berkeley": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=BK",
                "custom_catalog",
            ),
            "University of California, Irvine": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=IR",
                "custom_catalog",
            ),
            "University of California, Merced": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=MC",
                "custom_catalog",
            ),
            "University of California, Riverside": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=RV",
                "custom_catalog",
            ),
            "University of California, San Diego": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=SD",
                "custom_catalog",
            ),
            "University of California, San Francisco": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=SF",
                "custom_catalog",
            ),
            "University of California, Santa Barbara": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=SB",
                "custom_catalog",
            ),
            "University of California, Santa Cruz": (
                "https://techtransfer.universityofcalifornia.edu/default?campus=SC",
                "custom_catalog",
            ),
            "University of California System": (
                "https://techtransfer.universityofcalifornia.edu/default",
                "custom_catalog",
            ),
            "University of Iowa Research Foundation": (
                "https://uiowa.flintbox.com/categories",
                "custom_catalog",
            ),
            "University of Wisconsin-Madison/Wisconsin Alumni Research Foundation": (
                "https://www.warf.org/commercialize/technologies/",
                "custom_catalog",
            ),
        }

        for institution_name, (expected_url, expected_source_type) in expected.items():
            response = build_preferred_catalog_response(
                PreferredCatalogRequest(
                    institution_name=institution_name,
                    aggregate_source_url="https://www.canberra-ip.com/rss",
                    aggregate_source_type="inteum_rss",
                )
            )

            self.assertEqual(response.resolution_status, "direct-match")
            self.assertEqual(response.selected_url, expected_url)
            self.assertEqual(response.selected_source_type, expected_source_type)

    def test_resolves_to_fallback_when_direct_registry_missing(self) -> None:
        response = build_preferred_catalog_response(
            PreferredCatalogRequest(
                institution_name="California Institute of Technology",
                aggregate_source_url="https://www.canberra-ip.com/rss",
                aggregate_source_type="inteum_rss",
            )
        )

        self.assertEqual(response.resolution_status, "fallback-only")
        self.assertEqual(response.selected_url, "https://www.canberra-ip.com/rss")
        self.assertEqual(response.selected_source_type, "inteum_rss")


if __name__ == "__main__":
    unittest.main()