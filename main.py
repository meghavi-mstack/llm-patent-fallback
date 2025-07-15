"""
Simple Patent Search - Main entry point.
Combines OpenAI patent search with title similarity verification.
"""
import json
import sys
from typing import Dict, Any
from config import Config
from patent_search import PatentSearcher
from title_verification import TitleVerifier


def run_patent_search(compound: str) -> Dict[str, Any]:
    """
    Run the complete patent search and verification process.
    
    Args:
        compound: Chemical compound to search for
        
    Returns:
        Dictionary with search results and statistics
    """
    print("🚀" + "=" * 60)
    print("🚀 SIMPLE PATENT SEARCH STARTING")
    print("🚀" + "=" * 60)
    print(f"🧪 Compound: {compound}")
    print(f"🎯 Max patents: {Config.MAX_PATENTS}")
    print(f"📊 Similarity threshold: {Config.SIMILARITY_THRESHOLD}")
    print(f"🤖 Model: {Config.OPENAI_MODEL}")
    print("=" * 70)
    
    try:
        # Validate configuration
        Config.validate()
        print("✅ Configuration validated")
        
        # Step 1: Search for patents using OpenAI
        print("\n" + "=" * 50)
        print("STEP 1: PATENT SEARCH")
        print("=" * 50)
        
        searcher = PatentSearcher()
        patents = searcher.search_patents(compound)
        
        if not patents:
            print("❌ No patents found")
            return {
                "compound": compound,
                "patents_found": 0,
                "patents_verified": 0,
                "verified_patents": [],
                "success": False,
                "message": "No patents found by OpenAI search"
            }
        
        # Step 2: Verify patents with title similarity matching
        print("\n" + "=" * 50)
        print("STEP 2: TITLE VERIFICATION")
        print("=" * 50)
        
        verifier = TitleVerifier()
        verified_patents = verifier.verify_patents(patents, compound)
        
        # Generate final results
        results = {
            "compound": compound,
            "patents_found": len(patents),
            "patents_verified": len(verified_patents),
            "verified_patents": verified_patents,
            "success": True,
            "output_file": Config.get_output_path(compound)
        }
        
        # Print summary
        print("\n" + "🎉" * 50)
        print("SEARCH COMPLETE")
        print("🎉" * 50)
        print(f"📋 Patents found: {len(patents)}")
        print(f"✅ Patents verified: {len(verified_patents)}")
        print(f"📊 Success rate: {len(verified_patents)/len(patents)*100:.1f}%")
        print(f"💾 Results saved to: {results['output_file']}")
        
        if verified_patents:
            print("\n📋 VERIFIED PATENTS:")
            for i, patent in enumerate(verified_patents):
                print(f"  {i+1}. {patent['patent_id']} - {patent['title'][:60]}...")
                print(f"     Relevancy: {patent['relevancy']}")
                print(f"     Similarity: {patent['similarity_score']:.3f}")
        
        return results
        
    except Exception as e:
        error_msg = f"❌ Critical error: {e}"
        print(error_msg)
        return {
            "compound": compound,
            "patents_found": 0,
            "patents_verified": 0,
            "verified_patents": [],
            "success": False,
            "error": str(e)
        }


def main():
    """Main function for command line usage."""
    if len(sys.argv) != 2:
        print("Usage: python main.py '<compound_name>'")
        print("Example: python main.py '3-(trifluoromethyl)pyridine-4-carboxamide'")
        sys.exit(1)
    
    compound = sys.argv[1]
    results = run_patent_search(compound)
    
    if results["success"]:
        print(f"\n✅ Search completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Search failed: {results.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
