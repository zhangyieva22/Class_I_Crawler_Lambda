import requests
from scrapy import Selector
import time
import re

class GetProductCodeData:
    def __init__(self, product_code):
        self.product_code = product_code
        self.url = self.generate_url()
        self.selector = self.fetch_html()
        # print("----> URL:", self.url)
        # print("----> Selector:", self.selector)

    def generate_url(self):
        if isinstance(self.product_code, str) and self.product_code.isalpha():
            return f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id={self.product_code}"
        raise ValueError(f"Invalid product code: {self.product_code}")

    def fetch_html(self, retries=3, delay=5):
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
                    raise RuntimeError(
                        f"Failed to fetch data for product code {self.product_code}"
                    ) from e

    def extract_with_default(self, query, default='N/A'):
        if self.selector:
            result = self.selector.xpath(query).extract_first()
            result = self._clean_text(result)
            return result or default
        return default
    
    def _get_premarket_review(self):
        xpath = "//tr/th[text()='Premarket Review']/following-sibling::td[1]//text()"
        elements = self.selector.xpath(xpath)
        premarket_review_items = []
        temp_element = ""

        for element in elements:
            if (cleaned_text := self._clean_text(element.extract())):  # Only process non-empty cleaned texts
                if cleaned_text.endswith(('.', ')')):  # End of an entry
                    temp_element += f" {cleaned_text}"
                    if temp_element.strip():  # Ensure non-empty before adding
                        premarket_review_items.append(temp_element.strip())
                    temp_element = ""  # Reset for the next entry
                else:
                    temp_element += f" {cleaned_text}"

        # Check if there is any residual data to be added and it's not empty
        if temp_element.strip():
            premarket_review_items.append(temp_element.strip())

        return premarket_review_items or 'N/A'
    
    def _get_recognized_consensus_standards(self):
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
        return recognized_consensus_standards or 'N/A'


    def get_data(self):
        data =  {
            "device": self.extract_with_default("//tr/th[text()='Device']/following-sibling::td[1]/text()").title(),
            "regulation_description": self.extract_with_default("//tr/th[text()='Regulation Description']/following-sibling::td[1]/text()"),
            "definition": self.extract_with_default("//tr/th[text()='Definition']/following-sibling::td[1]/text()"),
            "physical_state": self.extract_with_default("//tr/th[text()='Physical State']/following-sibling::td[1]/text()"),
            "technical_method": self.extract_with_default("//tr/th[text()='Technical Method']/following-sibling::td[1]/text()"),
            "target_area": self.extract_with_default("//tr/th[text()='Target Area']/following-sibling::td[1]/text()"),
            "regulation_medical_specialty": self.extract_with_default("//tr/th[text()='Regulation Medical Specialty']/following-sibling::td[1]/text()"),
            "review_panel": self.extract_with_default("//tr/th[text()='Review Panel']/following-sibling::td[1]/text()").strip(),
            "product_code": self.extract_with_default("//tr/th[text()='Product Code']/following-sibling::td[1]/text()"),
            "premarket_review": self._get_premarket_review(),
            "submission_type": self.extract_with_default("//tr/th[text()='Submission Type']/following-sibling::td[1]/text()").strip(),
            "regulation_number": self.extract_with_default("//tr/th[text()='Regulation Number']/following-sibling::td[1]/a/text()"),
            "device_class": self.extract_with_default("//tr/th[text()='Device Class']/following-sibling::td[1]/text()").strip(),
            "gmp_exempt": self.extract_with_default("//tr/th[text()='GMP Exempt?']/following-sibling::td[1]/text()").strip(),
            "summary_malfunction_reporting": self.extract_with_default("//tr/th[text()='Reporting']/following-sibling::td[1]/text()"),
            "implanted_device": self.extract_with_default("//tr/th[contains(text(), 'Implanted Device?')]/following-sibling::td[1]/text()").strip(),
            "life_sustain_support_device": self.extract_with_default("//tr/th[contains(text(), 'Life-Sustain/Support Device?')]/following-sibling::td[1]/text()").strip(),
            "recognized_consensus_standards": self._get_recognized_consensus_standards(),
            "url": self.url
        }
        return self._validate_data(data)

    def _clean_text(self, text):
        """
        Clean the input text by replacing non-breaking spaces, carriage returns, newlines,
        and tabs with regular spaces, then strip any leading/trailing whitespace.
        Finally, capitalize only the first letter of the entire string.
        """
        if text:
            cleaned_text = re.sub(r'[\xa0\r\n\t]+', ' ', text).strip()
            # Capitalize only the first letter of the entire string
            return cleaned_text[0].upper() + cleaned_text[1:] if cleaned_text else ''
        return text
    
    def _validate_data(self, data):
        # Exclude 'url' from the check
        fields_to_check = {key: value for key, value in data.items() if key != 'url'}

        if all(value == 'N/A' or (isinstance(value, list) and value == ['N/A']) for value in fields_to_check.values()):
            return None
        return data
    

def main():
    product_code = "KWK" #aab
    print("------> Product code:", product_code)
    try:
        data = GetProductCodeData(product_code).get_data()
        print(f"Extracted ClassI Data: {data}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
