from googleapiclient.discovery import build
from urllib.parse import urlparse
from typing import List
import json


class ReliableSourceSearcher:
    def __init__(self, api_key: str, cse_id: str, reliable_domains: List[str]):
        self.service = build("customsearch", "v1", developerKey=api_key)
        self.cse_id = cse_id
        self.reliable_domains = reliable_domains

    def search_reliable_sources(self, query: str, num_results: int = 3) -> str:
        try:
            # Execute search
            result = self.service.cse().list(
                q=query,
                cx=self.cse_id,
                num=num_results * 2,
                fields='items(title,link,snippet,pagemap/metatags/og:description,pagemap/metatags/description)',  # Request additional fields
                # Alternative: you can use exactTerms=query to get more relevant snippets
                prettyPrint=True  # Makes the response more readable
            ).execute()

            reliable_results = []
            for item in result.get('items', []):
                domain = urlparse(item['link']).netloc

                # Extract date from pagemap if available
                date = None
                if 'pagemap' in item:
                    metatags = item['pagemap'].get('metatags', [{}])[0]
                    newsarticle = item['pagemap'].get('newsarticle', [{}])[0]

                    # Try different date fields
                    date = (metatags.get('og:published_time') or
                            metatags.get('article:published_time') or
                            metatags.get('publishedDate') or
                            metatags.get('date') or
                            newsarticle.get('datePublished'))

                # Get the longest available description
                description = item.get('snippet', '')
                if 'pagemap' in item:
                    metatags = item['pagemap'].get('metatags', [{}])[0]
                    og_desc = metatags.get('og:description', '')
                    meta_desc = metatags.get('description', '')

                    # Use the longest available description
                    description = max([description, og_desc, meta_desc], key=len)

                reliable_results.append({
                    'title': item['title'],
                    'link': item['link'],
                    'snippet': description,
                    'source': domain,
                    'date': date
                })

            return json.dumps({
                'query': query,
                'results': reliable_results
            }, indent=2)

        except Exception as e:
            return f"Error searching reliable sources: {str(e)}"
