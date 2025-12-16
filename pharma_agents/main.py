# main.py
import os
from dotenv import load_dotenv
from master_agent import MasterAgent

load_dotenv()


def main():
    # Example query from portfolio planner
    user_query = (
        "Evaluate the innovation opportunity for imatinib in obesity. "
    )

    master = MasterAgent()
    result = master.run(user_query)

    print("\n" + "="*70)
    print("FINAL ANSWER")
    print("="*70)
    print(result["final_answer"])

    # Display download link
    report_meta = result["report"]
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    if "download_link" in report_meta:
        download_link = report_meta["download_link"]
        if download_link.startswith("/"):
            full_download_url = f"{api_base_url}{download_link}"
        else:
            full_download_url = download_link
        
        print("\n" + "="*70)
        print("📥 DOWNLOADABLE REPORT LINK")
        print("="*70)
        print(f"\n🔗 {full_download_url}\n")
        print(f"Report ID: {report_meta.get('report_id', 'N/A')}")
        print(f"Report Type: {report_meta.get('report_type', 'N/A')}")
        print(f"Topic: {report_meta.get('topic', 'N/A')}")
        if 'file_size_mb' in report_meta:
            print(f"File Size: {report_meta['file_size_mb']} MB")
        if 'page_count' in report_meta:
            print(f"Pages: {report_meta['page_count']}")
        print("="*70)
    else:
        print("\n=== REPORT METADATA ===")
        print(report_meta)


if __name__ == "__main__":
    main()
#hello
