import requests
from scrapy import Selector
import time
import re

class GetData:
    def __init__(self, product_code):
        self.product_code = product_code
        self.url = self.generate_url()
        self.selector = self.fetch_html()
        print("----> url %s \n" % self.url)
        # print("----> selector %s \n" % self.selector)
    
    def generate_url(self):
        if isinstance(self.product_code, str) and self.product_code.isalpha():
            return f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id={self.product_code}"
        raise ValueError(f"Invalid product code: {self.product_code}")

    def fetch_html(self, retries=3, delay=5):
        """Fetch HTML with retries, including product code in error messages."""
        for attempt in range(retries):
            try:
                response = requests.get(self.url)
                response.raise_for_status()
                return Selector(text=response.text)
            except requests.RequestException as e:
                if attempt < retries - 1:
                    print(f"Attempt {attempt+1} for product code {self.product_code} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"All attempts for product code {self.product_code} failed: {e}")
                    raise

    def extract_with_default(self, query, default='N/A'):
        """Extract text with a default from Selector, handle missing selector."""
        if self.selector is not None:
            result = self.selector.xpath(query).extract_first()
            result = self.clean_text(result)
            return result if result else default
        else:
            return default

    # ClassI data extraction - 13 fields
    def get_classI_data(self):

        return {
            "device": self.extract_with_default("//tr/th[text()='Device']/following-sibling::td[1]/text()").title(),
            "regulation_description": self.extract_with_default("//tr/th[text()='Regulation Description']/following-sibling::td[1]/text()"),
            "definition":self.extract_with_default("//tr/th[text()='Definition']/following-sibling::td[1]/text()"),
            "physical_state": self.extract_with_default("//tr/th[text()='Physical State']/following-sibling::td[1]/text()"),
            "technical_method": self.extract_with_default("//tr/th[text()='Technical Method']/following-sibling::td[1]/text()"),
            "target_area": self.extract_with_default("//tr/th[text()='Target Area']/following-sibling::td[1]/text()"),
            "regulation_medical_specialty": self.extract_with_default("//tr/th[text()='Regulation Medical Specialty']/following-sibling::td[1]/text()"),
            "review_panel": self.extract_with_default("//tr/th[text()='Review Panel']/following-sibling::td[1]/text()").strip(),
            "product_code": self.extract_with_default("//tr/th[text()='Product Code']/following-sibling::td[1]/text()"),
            "premarket_review": self._get_class_I_premarket_review(),
            "submission_type": self.extract_with_default("//tr/th[text()='Submission Type']/following-sibling::td[1]/text()").strip(),
            "regulation_number": self.extract_with_default("//tr/th[text()='Regulation Number']/following-sibling::td[1]/a/text()"),
            "device_class": self.extract_with_default("//tr/th[text()='Device Class']/following-sibling::td[1]/text()").strip(),
            "gmp_exempt": self.extract_with_default("//tr/th[text()='GMP Exempt?']/following-sibling::td[1]/text()").strip(),
            "summary_malfunction_reporting": self.extract_with_default("//tr/th[text()='Reporting']/following-sibling::td[1]/text()"),
            "implanted_device": self.extract_with_default("//tr/th[contains(text(), 'Implanted Device?')]/following-sibling::td[1]/text()").strip(),
            "life_sustain_support_device": self.extract_with_default("//tr/th[contains(text(), 'Life-Sustain/Support Device?')]/following-sibling::td[1]/text()").strip(),
            "recognized_consensus_standards": self._get_class_I_recognized_consensus_standards(),
            "url": self.url
        }
    
    def clean_text(self, text):
        """
        Clean the input text by replacing non-breaking spaces, carriage returns, newlines,
        and tabs with regular spaces, and then stripping any leading/trailing whitespace.
        """
        if text:
            return text.replace(u'\xa0', u' ').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ').strip()
        return text
    
    def get_p_number_data(self):
        return
    
    def get_k_number_data(self):
        return
    
    def get_den_number_data(self):
        return  
    

    def _get_class_I_recognized_consensus_standards(self):
        recognized_consensus_standards = []
        standards = self.selector.xpath("//td/strong[text()='Recognized Consensus Standards']/following-sibling::table//li")

        for standard in standards:
            number = standard.xpath("./text()").extract_first()
            description = standard.xpath("./a/text()").extract_first()
            if number and description:
                # Replace non-breaking spaces with regular spaces and strip any leading/trailing whitespace
                number = number.replace(u'\xa0', u' ').strip()
                description = description.replace(u'\xa0', u' ').strip()
                recognized_consensus_standards.append(f"{number} {description}")

        if not recognized_consensus_standards:
            recognized_consensus_standards = 'N/A'
        return recognized_consensus_standards
    
    def _get_class_I_premarket_review(self):
        # Extract Premarket Review information
        premarket_review = []
        premarket_review_sections = self.selector.xpath("//tr/th[text()='Premarket Review']/following-sibling::td[1]//text()").extract()

        # Combine adjacent text nodes and clean up the text
        combined_section = ' '.join(premarket_review_sections).replace(u'\xa0', u' ').strip()
        # Split the combined text into separate items based on a pattern (e.g., recognizing line breaks and multiple spaces)
        premarket_review_items = combined_section.split('  ')  # Double space used as a delimiter for simplicity

        # Clean up each item
        for item in premarket_review_items:
            if (cleaned_item := ' '.join(item.split()).strip()):
                premarket_review.append(cleaned_item)

        # if not premarket_review:
        #     premarket_review = 'N/A'
        return premarket_review


def main():
    # Sample product code for testing
    product_code = "OZH"  # Replace with a valid product code
    print("Product code")
    try:
        # Instantiate the GetData class
        data_fetcher = GetData(product_code)

        # Fetch and print ClassI data
        classI_data = data_fetcher.get_classI_data()
        print(f"Extracted ClassI Data: {classI_data}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()