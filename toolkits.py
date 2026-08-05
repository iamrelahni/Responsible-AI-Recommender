# Each toolkit: (ID, name, B, C, D, E, SI, AG, family)
# family: 0 = Technical & Documentation, 1 = Governance & Risk-Management, 2 = Lifecycle & Procurement
TOOLKITS = [
    ("T01","Microsoft Responsible Innovation",1.27,0.75,1.7,0.75,1.8,0.5,2),
    ("T02","Data Ethics Framework",1.64,1.75,1.7,0.5,1.6,1.83,2),
    ("T03","Datasheets for Datasets",0.91,1.25,1.3,0.88,1.0,1.17,0),
    ("T04","Consequence Scanning",0.82,0.75,0.8,1.5,1.4,0.83,2),
    ("T05","Model Cards for Model Reporting",0.91,1.25,1.3,0.88,1.2,1.17,0),
    ("T06","Deon",1.09,1.75,1.5,1.0,1.2,1.33,2),
    ("T07","AI Fairness 360",0.82,1.25,0.7,1.38,1.2,0.5,0),
    ("T08","PAIR What-If Tool",0.91,1.0,1.1,1.12,1.0,0.33,0),
    ("T09","AI Procurement in a Box",1.36,1.75,1.5,1.25,1.4,2.0,1),
    ("T10","Ethically Aligned Design",1.82,1.25,1.6,0.75,1.6,1.33,1),
    ("T11","Aequitas",0.82,1.25,1.0,1.25,1.2,1.0,0),
    ("T12","Algorithmic Impact Assessment",1.27,1.25,1.4,0.88,2.0,2.0,2),
    ("T13","Ethics & Algorithms Toolkit",0.91,1.25,1.4,1.25,1.4,1.5,2),
    ("T14","Data Ethics Canvas",1.09,1.25,1.4,1.38,1.4,1.0,2),
    ("T15","Explaining decisions made with AI",1.55,1.75,1.9,1.25,1.6,1.67,1),
    ("T16","The Aletheia Framework",1.45,1.5,1.8,1.38,1.4,2.0,1),
    ("T17","Ethical Assessment of AI for Entrepreneurial Ecosystem",1.55,1.5,1.4,1.38,1.6,1.0,2),
    ("T18","JUST AI reflection prototype",0.73,0.0,0.6,0.88,1.8,0.17,2),
    ("T19","Responsible AI Diagnostic",1.36,1.75,1.8,1.12,1.0,2.0,1),
    ("T20","Ethical OS Toolkit",1.18,0.75,1.1,1.5,1.6,1.0,2),
    ("T21","AI Risk Management Framework",1.91,2.0,2.0,1.25,2.0,2.0,1),
    ("T22","ALTAI",1.91,1.75,1.9,1.38,1.8,2.0,1),
    ("T23","ISO/IEC 42001",1.64,2.0,1.8,0.88,1.4,2.0,1),
    ("T24","ISO/IEC 23894",1.27,1.5,1.7,0.88,1.2,2.0,1),
    ("T25","Responsible AI Standard v2",1.82,2.0,1.9,1.38,1.4,1.83,1),
    ("T26","Credo AI Governance Platform",1.27,1.75,1.8,1.25,1.4,2.0,1),
    ("T27","Holistic AI Governance Platform",1.27,1.75,1.9,1.5,1.4,2.0,1),
    ("T28","Secure AI Framework (SAIF)",0.55,1.75,0.9,1.5,0.4,1.67,0),
    ("T29","AI FactSheets / watsonx.governance",1.36,1.75,1.8,1.12,1.4,2.0,1),
    ("T30","AI and Data Protection Risk Toolkit",1.45,2.0,1.7,1.5,1.6,1.83,2),
    ("T31","OECD Classification Framework",1.0,1.75,1.2,1.0,1.2,0.83,2),
    ("T32","AI Verify",1.45,1.25,1.8,1.62,1.4,1.5,0),
]

FAMILY_NAMES = {0: "Technical & Documentation", 1: "Governance & Risk-Management", 2: "Lifecycle & Procurement"}
GROUPS = ["B","C","D","E","SI","AG"]  # the six score columns, in order

if __name__ == "__main__":
    from collections import Counter
    counts = Counter(t[8] for t in TOOLKITS)
    for fam_id, name in FAMILY_NAMES.items():
        print(f"Family {fam_id} ({name}): {counts[fam_id]} toolkits")
