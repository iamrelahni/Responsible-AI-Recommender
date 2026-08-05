import streamlit as st
from toolkits import GROUPS, FAMILY_NAMES
from info_gain import build_categorical_dataset
from tree import build_tree
from rank import recommend, print_shortlist
from descriptions import DESCRIPTIONS
from urls import TOOLKIT_URLS

st.set_page_config(page_title="RAIR - AI Toolkit Recommender", page_icon="🧭", layout="centered")

# Train the tree once per session (fast - 32 toolkits, shallow tree)
@st.cache_resource
def get_tree():
    data = build_categorical_dataset()
    return build_tree(data, list(GROUPS))

tree = get_tree()

st.title("🧭 RAIR: Readiness-Aware AI Toolkit Recommender")
st.caption("Answers a few short questions, then matches you to ethical-AI toolkits "
           "based on real evidence, not a generic best-seller list.")

st.divider()

with st.form("questions"):
    st.subheader("Tell us about your situation")

    q1 = st.radio(
        "1. Where are you in your AI journey right now?",
        options=["exploring", "building", "deployed", "multiple_systems"],
        format_func=lambda v: {
            "exploring": "Just exploring / considering AI (reading up, not using anything yet)",
            "building": "Actively building or piloting an AI system (e.g. testing a chatbot with a few staff or customers)",
            "deployed": "Already have AI in production (e.g. a tool is live and used by customers or staff day to day)",
            "multiple_systems": "Have multiple AI systems in use (AI is embedded in several parts of the business)",
        }[v],
    )

    q2 = st.radio(
        "2. Which best describes how your organisation currently handles AI-related decisions?",
        options=["ad_hoc", "informal", "written_inconsistent", "formal_audited"],
        format_func=lambda v: {
            "ad_hoc": "No formal process, decisions are made ad hoc (whoever's using it just makes their own call)",
            "informal": "Some informal practices, nothing written down (e.g. people know to double-check outputs, but there's no policy)",
            "written_inconsistent": "We have written policies but don't consistently follow them (a policy exists on paper, but people don't always stick to it)",
            "formal_audited": "We have a formal, documented, and audited process (clear rules, sign-off, and regular checks)",
        }[v],
    )

    q3 = st.radio(
        "3. What's the biggest worry driving you to look into this?",
        options=["fairness", "explainability", "privacy", "security", "compliance", "trust"],
        format_func=lambda v: {
            "fairness": "Treating people/customers fairly, avoiding bias (e.g. worried the system might favour some groups over others)",
            "explainability": "Being able to explain AI decisions to customers or regulators (e.g. someone asks 'why was I turned down' and you need a real answer)",
            "privacy": "Protecting data and privacy (e.g. making sure personal or customer data isn't misused or exposed)",
            "security": "Security or misuse of the system (e.g. someone tricking the system, or a data breach)",
            "compliance": "Meeting legal/regulatory requirements (e.g. GDPR, the EU AI Act, or industry rules)",
            "trust": "Building trust with the public or stakeholders (e.g. customers, investors, or the public feeling confident in how you use AI)",
        }[v],
    )

    q4 = st.radio(
        "4. What can you realistically commit to this right now?",
        options=["just_my_time", "small_budget", "dedicated_team_limited_budget", "team_and_budget"],
        format_func=lambda v: {
            "just_my_time": "Just my own time, no budget (you're doing this on top of your normal job, nothing set aside to spend)",
            "small_budget": "A small amount of budget, no dedicated team (e.g. a few hundred/thousand pounds, no one owns this full-time)",
            "dedicated_team_limited_budget": "A dedicated person or small team, limited budget (someone's job includes this, but funds are tight)",
            "team_and_budget": "A dedicated team and budget for tools/consulting (you could hire help or pay for software if needed)",
        }[v],
    )

    q5 = st.radio(
        "5. Do you have anyone in-house with relevant expertise (data, compliance, AI)?",
        options=["none", "technical_only", "compliance_only", "both"],
        format_func=lambda v: {
            "none": "No one (nobody in-house knows much about data, AI, or compliance)",
            "technical_only": "Some technical skill, no compliance/governance background (e.g. someone who can code, but no one handles legal/policy)",
            "compliance_only": "Some compliance/legal background, limited technical skill (e.g. someone handles policy/legal, but no one builds or codes)",
            "both": "Both technical and compliance expertise available (you have people who can cover both sides)",
        }[v],
    )

    q6 = st.radio(
        "6. Is this about one specific AI system/decision, or your organisation's AI use in general?",
        options=["specific_system", "general_approach"],
        format_func=lambda v: {
            "specific_system": "One specific system or use case (e.g. a single chatbot, recommendation engine, or hiring tool)",
            "general_approach": "Our general approach to AI across the business (thinking about AI use as a whole, not just one tool)",
        }[v],
    )

    submitted = st.form_submit_button("Get my recommendations", use_container_width=True)

if submitted:
    st.divider()
    tiers = recommend(tree, q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6)

    if not tiers:
        st.warning("Something went wrong generating recommendations. Please try again.")
    elif tiers[0][0].get("is_fallback"):
        st.subheader("Your recommendation")
        st.info(
            "Your specific combination of answers doesn't closely match any toolkit "
            "in our scored dataset. This is an honest gap in the data, not an error. "
            "Rather than guess, we're recommending a broad, well-established framework "
            "that suits almost any organisation as a starting point.",
            icon="ℹ️",
        )
        c = tiers[0][0]
        with st.container(border=True):
            st.markdown(f"**{c['id']}: {c['name']}**")
            st.caption(f"Family: {c['family']}")
            st.write(DESCRIPTIONS.get(c['id'], ''))
            if "now" in c["sequencing"]:
                st.success("Fits your current stage, use this now", icon="✅")
            if "next" in c["sequencing"]:
                st.info("Also relevant for your next stage", icon="➡️")
            st.write(c["evidence"])
            url = TOOLKIT_URLS.get(c['id'], '')
            if url:
                st.markdown(f"🔗 [Find this toolkit here]({url})")
    else:
        st.subheader("Your recommendations")
        st.caption("Toolkits are grouped into tiers. Every toolkit within a tier scored "
                   "equally on your stated priority. Where the evidence is genuinely tied, "
                   "we show you all the options rather than guessing at an order.")

        for tier_num, tier in enumerate(tiers[:2], 1):
            rep = tier[0]
            families = sorted(set(c["family"] for c in tier))
            st.markdown(f"#### Tier {tier_num}: {rep['family_p']:.0%} match confidence, "
                        f"{rep['fit']:.0%} fit to your stated priority")
            st.caption(f"Spans: {', '.join(families)}")

            for c in tier:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{c['id']}: {c['name']}**")
                        st.caption(f"Family: {c['family']}")
                        st.write(DESCRIPTIONS.get(c['id'], ''))
                        if "now" in c["sequencing"]:
                            st.success("Fits your current stage, use this now", icon="✅")
                        if "next" in c["sequencing"]:
                            st.info("Also relevant for your next stage", icon="➡️")
                        if not c["sequencing"]:
                            st.caption("⚠️ Not strongly matched to your current or next lifecycle stage")
                        st.write(c["evidence"])
                        url = TOOLKIT_URLS.get(c['id'], '')
                        if url:
                            st.markdown(f"🔗 [Find this toolkit here]({url})")
                    with col2:
                        st.metric("Overall breadth", f"{c['overall']:.0%}")

        with st.expander("How were these ranked? (full transparency)"):
            st.write(
                "1. Your answers to Q1, Q2, Q4 and Q5 were converted into an estimated "
                "profile across six criteria groups (Ethics, Lifecycle, Responsible-AI, "
                "Usability, Stakeholder Impact, Governance).\n\n"
                "2. That profile was run through a decision tree trained on 32 real, "
                "evidence-scored toolkits, producing a probability for each toolkit family.\n\n"
                "3. Your answer to Q6 (scope) adjusted those probabilities.\n\n"
                "4. Within the matched famil(ies), toolkits were ranked purely by how well "
                "they scored on your stated priority (Q3), not blended with their overall "
                "score, so a toolkit that specialises in exactly what you need isn't "
                "penalised for being narrow.\n\n"
                "5. Toolkits that scored identically are shown together as a tier, with "
                "their own evidence, so you can make the final call yourself."
            )
