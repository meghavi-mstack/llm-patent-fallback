"""
OpenAI-based patent search functionality.
"""
import json
from typing import List, Dict, Any
from openai import OpenAI
from config import Config


class PatentSearcher:
    """Handles patent search using OpenAI API."""
    
    def __init__(self):
        """Initialize the patent searcher."""
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            timeout=Config.OPENAI_TIMEOUT
        )
    
    def search_patents(self, compound: str) -> List[Dict[str, Any]]:
        """
        Search for patents related to a chemical compound using OpenAI.
        
        Args:
            compound: Chemical compound to search for
            
        Returns:
            List of patent dictionaries with patent_id, title, and relevancy
        """
        print(f"🔍 Searching for patents related to: {compound}")
        
        # Build the search prompt
        prompt = self._build_search_prompt(compound)
        
        try:
            print("🤖 Calling OpenAI API...")
            response = self.client.responses.create(
                model=Config.OPENAI_MODEL,
                tools=[{
                    "type": "web_search_preview",
                    "search_context_size": "high",
                }],
                input=prompt,
            )

            response_text = response.output_text.strip()
            print(f"✅ Received response ({len(response_text)} characters)")

            # Parse JSON response
            patents_data = json.loads(response_text)
            patents = patents_data.get("patents", [])

            print(f"📋 Found {len(patents)} patents")
            return patents
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            return []
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return []
    
    def _build_search_prompt(self, compound: str) -> str:
        """Build the search prompt for OpenAI."""
        return f"""
You are an expert at finding the most relevant patents given a chemical compound with their patent ids.

### Guidelines to follow ####
- Given a compound you will first focus on getting all the patents which are specifically focusing on synthesis of the given compound (e.g: There is a direct mention on the synthesis of the compound in the Title, Abstract or Claim.)
- After this you will focus getting all the left patents that spend their good chunk on the synthesis of the given input compound (e.g: The compound synthesis is discussed in detail as an intermediate or any other case.)
- You will get patents from worldwide even if it is Chinese, US, Korean, Japanese or any other patent worldwide.
- The patents should be available easily on the internet for example on websites like Google Patents, Espacenet etc.
- You should strictly follow the rules and never create any patent by yourself. If you cannot find any patent do not give any patent in the output.
- You should validate your results with datasources and confirm that they are accurate, ignore the results if you don't have the source

##Output##
CRITICAL: You MUST respond with ONLY valid JSON in this exact format (no other text, no explanations, no markdown):
{{"patents": [
  {{"patent_id": "US1234567A", "title": "Synthesis of compound X", "relevancy": "High - Direct synthesis method described"}},
  ...
]}}

- The output should be a list of top {Config.MAX_PATENTS} most relevant patents specifically their patent ids, Relevant Section, Title.
- Never ever try to create a patent detail by yourself. If you cannot find a patent just don't give any result.
- If in any case you can find more than {Config.MAX_PATENTS} patents that fits the above criteria just output them all.
- RESPOND WITH ONLY THE JSON OBJECT - NO OTHER TEXT

Using all the above instructions give the results of the compound: "{compound}"
"""
