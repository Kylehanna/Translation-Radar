from datetime import date
import unittest

from translation_radar_api.sources.inteum_rss import parse_inteum_rss_feed


SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dataField="https://example.org/datafield">
  <channel>
    <title>Sample Inteum Feed</title>
    <item>
      <title>Targeted ADC linker platform</title>
      <description>Novel linker chemistry for antibody-drug conjugates.</description>
      <guid>tech-001</guid>
      <category>oncology</category>
      <category>adc</category>
      <pubDate>Fri, 09 May 2026 12:00:00 GMT</pubDate>
      <dataField:contactName>Jane Doe</dataField:contactName>
      <dataField:contactEmail>jane@example.edu</dataField:contactEmail>
      <dataField:ipStatus>patent pending</dataField:ipStatus>
      <dataField:technologyType>biotherapeutics</dataField:technologyType>
      <dataField:developmentStage>preclinical</dataField:developmentStage>
    </item>
  </channel>
</rss>
"""


class InteumRssParsingTests(unittest.TestCase):
    def test_parses_and_normalizes_feed_items(self) -> None:
        records = parse_inteum_rss_feed(
            feed_xml=SAMPLE_FEED,
            institution_name="Example University",
            source_url="https://example.edu/tech/feed.xml",
        )

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.institution_name, "Example University")
        self.assertEqual(record.source_type, "inteum_rss")
        self.assertEqual(record.title, "Targeted ADC linker platform")
        self.assertEqual(record.contact_email, "jane@example.edu")
        self.assertEqual(record.category_tags, ["oncology", "adc"])
        self.assertEqual(record.posted_on, date(2026, 5, 9))
        self.assertEqual(record.raw_metadata["ipStatus"], "patent pending")

    def test_parses_nested_canberra_style_metadata(self) -> None:
        feed = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\" xmlns:dataField=\"https://www.inteum.com/technologies/data/\">
  <channel>
    <title>Latest technologies from Canberra IP</title>
    <item>
      <title>A Weight-Bearing Highly Articulated Robotic Arm</title>
      <link>https://www.canberra-ip.com/tech/A_Weight-Bearing_Highly_Articulated_Robotic_Arm</link>
      <description><![CDATA[
        <p>A robotic arm capable of up to 100 different articulations.</p>
        <img alt=\"\" src=\"https://upenn.technologypublisher.com/files/sites/24-10779_image_02.jpg\" />
      ]]></description>
      <pubDate>Fri, 08 May 2026 15:50:44 GMT</pubDate>
      <author>lbricha@upenn.edu</author>
      <guid>https://www.canberra-ip.com/tech/A_Weight-Bearing_Highly_Articulated_Robotic_Arm</guid>
      <dataField:caseId>24-10779-tpNCS</dataField:caseId>
      <dataField:lastUpdateDate>Fri, 08 May 2026 15:56:41 GMT</dataField:lastUpdateDate>
      <dataField:brief>A robotic arm capable of up to 100 different articulations.</dataField:brief>
      <dataField:technology>To achieve a high number of articulations, the inventors designed each module.</dataField:technology>
      <dataField:docket>Docket #24-10779</dataField:docket>
      <dataField:inventorList>
        <dataField:inventor>
          <dataField:firstName>Mark</dataField:firstName>
          <dataField:lastName>Yim</dataField:lastName>
          <dataField:emailAddress>yim@seas.upenn.edu</dataField:emailAddress>
        </dataField:inventor>
      </dataField:inventorList>
      <dataField:licensingContactList>
        <dataField:licensingContact>
          <dataField:firstName>Robert</dataField:firstName>
          <dataField:lastName>Ljungberg</dataField:lastName>
          <dataField:emailAddress>robertlj@upenn.edu</dataField:emailAddress>
        </dataField:licensingContact>
      </dataField:licensingContactList>
      <dataField:categoryName><![CDATA[Technology Classifications > Materials| Technology Classifications > Robotics]]></dataField:categoryName>
    </item>
  </channel>
</rss>
"""

        records = parse_inteum_rss_feed(
            feed_xml=feed,
            institution_name="Canberra IP",
            source_url="https://www.canberra-ip.com/rss",
        )

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.institution_name, "University of Pennsylvania")
        self.assertEqual(record.contact_name, "Robert Ljungberg")
        self.assertEqual(record.contact_email, "robertlj@upenn.edu")
        self.assertEqual(
            record.category_tags,
            ["Technology Classifications > Materials", "Technology Classifications > Robotics"],
        )
        self.assertEqual(record.summary, "A robotic arm capable of up to 100 different articulations.")
        self.assertEqual(record.raw_metadata["origin_host"], "upenn.technologypublisher.com")
        self.assertEqual(record.raw_metadata["docket"], "Docket #24-10779")
        self.assertEqual(record.raw_metadata["inventors"][0]["lastName"], "Yim")


if __name__ == "__main__":
    unittest.main()