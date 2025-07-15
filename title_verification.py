"""
Patent title verification using web scraping and similarity matching.
"""
import json
import time
import requests
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from config import Config


class TitleVerifier:
    """Handles patent title verification through web scraping."""

    def __init__(self):
        """Initialize the title verifier."""
        self.session = requests.Session()
        # **CHANGE 2: ADD THE ACCEPT-LANGUAGE HEADER**
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })

    def verify_patents(self, patents: List[Dict[str, Any]], compound: str) -> List[Dict[str, Any]]:
        """
        Verify patents by checking actual titles and calculating similarity.

        Args:
            patents: List of patent dictionaries from OpenAI search
            compound: Chemical compound name for output file

        Returns:
            List of verified patent dictionaries
        """
        print(f"🔍 Verifying {len(patents)} patents...")
        verified_patents = []

        for i, patent in enumerate(patents):
            patent_id = patent.get('patent_id', '')
            claimed_title = patent.get('title', '')
            relevancy = patent.get('relevancy', '')

            print(f"📋 Verifying patent {i+1}/{len(patents)}: {patent_id}")

            # Get actual title from web
            actual_title = self._get_patent_title(patent_id)

            if actual_title is None:
                print(f"❌ Patent {patent_id} not found")
                continue

            # Calculate title similarity
            similarity = self._calculate_similarity(claimed_title, actual_title)
            print(f"📊 Title similarity: {similarity:.3f}")
            print(f"   Claimed: {claimed_title}")
            print(f"   Actual:  {actual_title}")

            # Check if title contains non-English characters (like Chinese)
            is_non_english = self._contains_non_english(actual_title)

            # Create patent entry regardless of similarity score
            verified_patent = {
                'patent_id': patent_id,
                'title': actual_title,  # Use actual title
                'relevancy': relevancy,
                'similarity_score': similarity,
                'verified': similarity >= Config.SIMILARITY_THRESHOLD
            }

            # Add language note if needed
            if is_non_english:
                verified_patent['language_note'] = 'Non-English title - similarity may be affected by language'

            verified_patents.append(verified_patent)

            if similarity >= Config.SIMILARITY_THRESHOLD:
                print(f"✅ Patent {patent_id} verified (similarity: {similarity:.3f})")
            else:
                print(f"⚠️ Patent {patent_id} saved with low similarity (similarity: {similarity:.3f})")

            # Save immediately to JSON
            self._save_verified_patent(verified_patent, compound)

            # Add delay between requests
            if i < len(patents) - 1:
                time.sleep(Config.REQUEST_DELAY)

        print(f"✅ Verification complete: {len(verified_patents)}/{len(patents)} patents verified")
        return verified_patents

    def _get_patent_title(self, patent_id: str) -> Optional[str]:
        """Fetch patent title from Google Patents."""
        # **CHANGE 1: ADD /en TO THE URL**
        url = f"https://patents.google.com/patent/{patent_id}/en"

        for attempt in range(Config.MAX_RETRIES):
            try:
                # Use the updated session headers here automatically
                response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Try to find title using itemprop="title"
                title_tag = soup.find('span', itemprop='title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    # Validate that it's actually a title, not an abstract
                    if self._is_valid_title(title):
                        return title

                # Fallback to h1 tag
                h1_tag = soup.find('h1', itemprop='pageTitle')
                if h1_tag:
                    full_title = h1_tag.get_text(strip=True)
                    # This cleanup is still useful
                    title = full_title.split(' - Google Patents')[0].replace(f"{patent_id} - ", "").strip()
                    if self._is_valid_title(title):
                        return title

                # If an English version doesn't exist, Google might 404.
                # If we get a page but no title, it's still a failure for this function.
                print(f"⚠️ Title tag not found on page for {patent_id}")
                return None

            except requests.exceptions.HTTPError as e:
                # Specifically handle 404 errors if the /en version doesn't exist
                if e.response.status_code == 404:
                    print(f"⚠️ English version (/en) not found for {patent_id}. It may only exist in its original language.")
                    return None # Explicitly return None on 404
                print(f"⚠️ Attempt {attempt + 1} failed for {patent_id} with HTTP error: {e}")
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed for {patent_id}: {e}")

            if attempt < Config.MAX_RETRIES - 1:
                time.sleep(1)

        return None # Return None after all retries fail

    def _calculate_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        title1_norm = title1.lower().strip()
        title2_norm = title2.lower().strip()
        return SequenceMatcher(None, title1_norm, title2_norm).ratio()

    def _contains_non_english(self, text: str) -> bool:
        """Check if text contains non-English characters (Chinese, Japanese, Korean, etc.)."""
        for char in text:
            # Chinese characters
            if '\u4e00' <= char <= '\u9fff':
                return True
            # Japanese Hiragana and Katakana
            if '\u3040' <= char <= '\u30ff':
                return True
            # Korean Hangul
            if '\uac00' <= char <= '\ud7af':
                return True
        return False

    def _is_valid_title(self, text: str) -> bool:
        """Check if the extracted text is a valid title (not an abstract or other content)."""
        if not text:
            return False

        # Check if it starts with "Abstract" (common issue)
        if text.lower().startswith('abstract'):
            print(f"⚠️ Detected abstract instead of title: {text[:50]}...")
            return False

        # Check if it's too long to be a title (likely an abstract or description)
        if len(text) > 300:
            print(f"⚠️ Text too long to be a title ({len(text)} chars): {text[:50]}...")
            return False

        # Check if it contains multiple sentences (likely an abstract)
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        if sentence_count > 2:
            print(f"⚠️ Text contains multiple sentences, likely not a title: {text[:50]}...")
            return False

        return True

    def _save_verified_patent(self, patent: Dict[str, Any], compound: str) -> None:
        """Save verified patent to JSON file."""
        try:
            output_path = Config.get_output_path(compound)

            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {"compound": compound, "verified_patents": []}

            existing_ids = {p.get('patent_id') for p in data.get('verified_patents', [])}
            if patent['patent_id'] not in existing_ids:
                data["verified_patents"].append(patent)

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"💾 Saved patent {patent['patent_id']} to {output_path}")

        except Exception as e:
            print(f"⚠️ Failed to save patent: {e}")