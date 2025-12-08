# main.py

from pprint import pprint

from master_agent import MasterAgent


def run_example():
    """
    Example orchestration run.

    You can later wire this into a web UI / chatbot front-end.
    """
    master = MasterAgent()

    # Example query from a portfolio planner:
    molecule = "Semaglutide"
    indication = "Obesity"

    print(f"=== Running evaluation for {molecule} in {indication} ===")
    result = master.evaluate_molecule(molecule=molecule, indication=indication)

    # Pretty-print some useful parts:
    print("\n=== Simple Summary ===")
    pprint(result["simple_summary"])

    print("\n=== Report Metadata ===")
    pprint(result["results"]["report"]["raw"])

    # You can also inspect individual agent raw outputs:
    # pprint(result["results"]["iqvia"]["raw"])


if __name__ == "__main__":
    run_example()