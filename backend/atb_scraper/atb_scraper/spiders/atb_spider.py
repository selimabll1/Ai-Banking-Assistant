import scrapy
import os

class AtbSpider(scrapy.Spider):
    name = 'atb_spider'
    allowed_domains = ['atb.tn']
    start_urls = [
        'https://www.atb.tn/produits/credit-sakan-presentation.php',
        'https://www.atb.tn/produits/credit-mounassib-presentation.php',
        # Add more URLs here
    ]

    def parse(self, response):
        # Extract title from headers (h1, h2, h3) inside container-main
        title = response.xpath('//div[@id="container-main"]//h1/text()').get() or \
                response.xpath('//div[@id="container-main"]//h2/text()').get() or \
                response.xpath('//div[@id="container-main"]//h3/text()').get() or \
                'Title not found'
        
        # Extract content (all paragraphs)
        content = response.xpath('//div[@id="container-main"]//p/text()').getall()
        content = "\n".join(content)

        # Clean title for valid filenames (avoid illegal characters like ':')
        title = "".join([c if c.isalnum() else "_" for c in title])

        # Saving content to file
        filename = f"{title}.txt"
        file_path = os.path.join('scraped_content', filename)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"=== {title} ===\n{content}\n")
        
        self.log(f'Saved file {filename}')
