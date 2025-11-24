import streamlit as st
import re
from openai import OpenAI

# --- NEW: Predefined Customer Segments ---
# Storing the three segments you provided in a structured list.
segments = [
    {
        "name": "セグメント1：子育て世帯 (Households with Children)",
        "audience": """
        日本在住の、乳幼児から小学生までの子供を持つ親。特に、子供の安全と心身の健康に対する責任感が強く、防災準備の必要性を感じているが、日々の多忙さから具体的な行動に移せていないことが多い。
        """,
        "pain_points": """
        - 「とにかく、この子を守りたい」： 物理的な安全確保（怪我をさせない）だけでなく、災害という非日常の恐怖や不安から子供の心を守りたい（精神的安定の維持）という根源的な欲求がある。
        - 「何を備えればいいか分からない」： 子供の成長ステージ（乳児期、幼児期、学齢期）によって必要なものが劇的に変化するため、情報のキャッチアップが追いつかず、準備が複雑で難しいと感じている。
        - 「非常食を食べてくれるか不安」： ストレス下で子供が普段食べ慣れないものを拒否する可能性を懸念している。特に、食物アレルギーを持つ子供の親にとっては、配給物資に頼れないため、安全な食料の個人備蓄は死活問題である。
        - 「避難所で子供が騒いだらどうしよう」： 長引く避難生活での子供の退屈やストレス、それに伴う周囲への迷惑を心配している。音の出ないおもちゃや絵本など、「心のケア」に繋がるアイテムを求めている。
        - 「もしも、はぐれてしまったら」： 親と離れて行動する時間が増える学齢期の子供を持つ親にとって、万が一の際の安否確認や、子供が一人で助けを求められるかどうかが最大の不安材料となっている。
        - 「防災用品の管理が面倒」： 備蓄品の賞味期限チェックや入れ替えといった定期的なメンテナンスが、時間的・精神的な負担になっている。
        """
    },
    {
        "name": "セグメント2：高齢者世帯 (Elderly Households)",
        "audience": """
        日本在住の高齢者、または高齢者のみで構成される世帯。加齢による身体機能の低下、持病、介護の必要性、デジタル機器への不慣れさなど、災害時に複合的な脆弱性を抱えている。
        """,
        "pain_points": """
        - 「持病の薬がなくなったら命に関わる」： 高血圧や糖尿病などの慢性疾患を持つ高齢者にとって、薬の確保は生命維持に直結する最優先事項である。お薬手帳の携帯も不可欠。
        - 「普通の非常食は食べられない」： 噛む力や飲み込む力（咀嚼・嚥下機能）が低下しており、乾パンやおにぎりのような固いものが食べられない。おかゆやムース状の介護食など、個々の状態に合わせた「やわらかい食事」が必須である。
        - 「停電したら情報が何も入らない」： 情報収集をテレビやラジオに大きく依存しているため、停電時に孤立し、避難情報などを得られなくなることへの強い不安がある（情報的脆弱性）。
        - 「避難所での生活は体にこたえる」： 硬い床での雑魚寝は身体への負担が大きく、体調の悪化や持病の再発に繋がりやすい。また、トイレを我慢することによる体調不良も懸念している。
        - 「いざという時に助けを呼べない」： 一人暮らしや地域社会との繋がりが希薄な場合、自力での避難や助けを求めることに困難を感じている（社会的脆弱性）。
        """
    },
    {
        "name": "セグメント3：高齢の親を持つ子供世代 (Adult Children with Elderly Parents)",
        "audience": """
        高齢の親と離れて暮らす40代〜50代の現役世代。親の安全を案じているが、自身の仕事や家庭で多忙なため、実家の防災対策まで手が回らないことにジレマを感じている。
        """,
        "pain_points": """
        - 「親のことが心配だが、何から手をつければ良いか分からない」： 親の健康状態（持病、食事制限など）に特化した防災準備の知識がなく、最適なものを選ぶことに困難を感じている。
        - 「実家の備蓄管理は、物理的に不可能」： 遠隔で備蓄品の賞味期限を管理し、定期的に入れ替えることは極めて負担が大きく、現実的ではないと感じている。
        - 「面倒なことは専門家に任せたい」： 親の安全を確保したいという気持ちはあるが、時間的・心理的な負担は最小限に抑えたい。「これを贈っておけば大丈夫」という、信頼できる専門家が監修した手軽なソリューションを求めている。
        - 「親不孝だと思われたくない」： 何も対策をしないことへの罪悪感や、万が一のことがあった際の後悔を恐れている。「離れていてもできる親孝行」として、防災準備を捉えている。
        """
    }
]

# --- Prompt Templates ---
def get_prompt_1(transcripts_data):
    """Builds the prompt for Step 1: Creative Analysis."""
    prompt = """
#Prompt 1: Creative Analysis

## AI ROLE
You are an expert Creative Director for SNS video content. Your specialty is deconstructing viral short-form videos to understand the underlying psychology and structural elements that make them successful.

## YOUR TASK
Analyze the provided YouTube Shorts transcripts and their summaries. Your goal is to identify and articulate the specific patterns and techniques that make this content effective and engaging. Go beyond the surface level and explain the "why" behind their success.

## VIDEO DATA TO ANALYZE
"""
    for i, transcript in enumerate(transcripts_data):
        prompt += f"\n### Video {i+1}:\n* Summary: [Summary for Video {i+1}]\n* Transcript:\n{transcript}\n"

    prompt += """
---
## ANALYSIS FRAMEWORK
For each video, and in your final summary, structure your analysis around these key points:
1.  *The Hook (8 Seconds):* What specific verbal or visual technique is used to immediately stop the viewer from scrolling? (e.g., posing a controversial question, showing a surprising result first, using a sound trigger).
2.  *Pacing and Information Density:* How is the information delivered? Is it rapid-fire? Is there a slow build-up to a punchline? Why is this pacing effective for the topic?
3.  *Emotional Core:* What is the primary emotion the video targets? (e.g., Curiosity, Humor, Anxiety/Relief, Awe, Relatability). How is this emotion created?
4.  *Relatability Factor:* What specific words, scenarios, or problems make the target audience think "this is for me"?
5.  *Value Delivery:* How does the video deliver its core message or "aha!" moment? Is it through a demonstration, a quick tip, a story, or a joke?

## DELIVERABLE
Produce a concise summary titled "## Key Success Patterns". This summary should synthesize your findings into a list of actionable creative principles we can apply to future videos.
"""
    return prompt

def get_prompt_2(key_patterns, audience, pain_points):
    """Builds the prompt for Step 2: Strategic Ideation."""
    return f"""
#Prompt 2: Strategic Ideation

## AI ROLE
You are a Creative Director and Brand Strategist, brainstorming a slate of new YouTube Shorts concepts. You must fuse proven creative formulas with specific customer insights.

## YOUR TASK
Generate 5 unique and compelling YouTube Shorts ideas. These ideas must directly address the defined customer needs and target audience segment below, while strategically incorporating the "Key Success Patterns" we've already identified.

## STRATEGIC INPUTS

### 1. Key Success Patterns:
{key_patterns}

### 2. New Campaign Focus:
* *Target Audience Segment:* {audience}
* *Core Customer Needs / Pain Points:* {pain_points}

---

## DELIVERABLE
Format your output as a list of 5 video ideas. For each idea, provide the following in this exact format:
* **Concept Title:** A short, catchy title.
* **Core Message:** The single, clear takeaway for the viewer.
* **Synopsis (1-2 sentences):** A brief description of what happens in the video.
* **Strategic Alignment:** Briefly explain how this idea leverages a specific "Success Pattern" (from your input) and solves a "Customer Need" (from your input).
"""

def get_prompt_3(chosen_idea):
    """Builds the prompt for Step 3: Multiple Script Generation."""
    return f"""
#Prompt 3: Multiple Script Generation (60 Seconds)

## AI ROLE
You are a highly versatile senior scriptwriter for a top digital marketing agency. Your task is to take a single creative concept and transform it into three (3) distinct, complete 60-second video scripts (台本) in Japanese. Each script should offer a different creative angle or narrative approach, while still adhering to the core idea and format, optimized for maximum viewer retention and impact.

## YOUR TASK
Generate three (3) detailed, production-ready scripts based on the video idea provided below. Each script must be unique in its execution but strictly adhere to the specified 60-second format and structure.

## CHOSEN VIDEO IDEA
* **Concept Title:** {chosen_idea['title']}
* **Core Message:** {chosen_idea['message']}
* **Synopsis:** {chosen_idea['synopsis']}

---

## REQUIRED SCRIPT FORMAT (For EACH of the 3 scripts)

* *Language:* Japanese
* *Total Length:* 60 seconds
* *Blueprint:* Each script must follow this four-part structure precisely:

    * *1. Hook (0-8 seconds):*
        * A high-impact opening that immediately grabs attention.
        * Must introduce a compelling problem, question, or surprising statement.
        * Include notes for on-screen captions (テロップ) and sound effects (SE).

    * *2. Problem / Story Development (8-45 seconds):*
        * This is the main body of the video.
        * Expand on the hook, building tension, telling the core story, or explaining the details of the problem.
        * This section should be paced well to maintain viewer interest, using a mix of information and relatable moments or humor.

    * *3. Climax / Solution (45-55 seconds):*
        * The key "aha!" moment or the main payoff for the viewer.
        * Clearly present the solution to the problem, the big reveal, or the satisfying conclusion to the story.

    * *4. Call to Action (55-60 seconds):*
        * A clear and direct instruction in the final moments.
        * *Text to use:* "さらに詳しい情報はプロフのリンクから" (For more details, check the link in my profile).

## DELIVERABLE
Generate three (3) distinct Japanese scripts (台本). Label each script clearly (e.g., "Script Option 1," "Script Option 2," "Script Option 3").
"""

# --- Helper Functions ---
def call_chatgpt(api_key, prompt_text, model="gpt-4o"):
    """
    Function to call the OpenAI API and get a response.
    """
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            max_tokens=15000,
            messages=[
                {"role": "system", "content": "You are a helpful assistant executing the user's request precisely."},
                {"role": "user", "content": prompt_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

def parse_ideas(ai_response_text):
    """
    Parses the raw text from the AI in Step 2 into a list of dictionaries.
    This new regex is more flexible to handle variations in AI output.
    """
    ideas = []
    # This pattern robustly finds each concept block and its components.
    pattern = re.compile(
        r"\*\*Concept Title:\*\*(.*?)\*\*Core Message:\*\*(.*?)\*\*Synopsis.*?\:\*\*(.*?)\*\*Strategic Alignment:\*\*(.*?)(?=\*\*Concept Title:\*\*|$)",
        re.DOTALL | re.IGNORECASE
    )
    matches = pattern.finditer(ai_response_text)
    for match in matches:
        ideas.append({
            "title": match.group(1).strip(),
            "message": match.group(2).strip(),
            "synopsis": match.group(3).strip(),
            "alignment": match.group(4).strip()
        })
    return ideas


# --- Streamlit App User Interface ---
st.set_page_config(layout="wide", page_title="AI Script Generator")
st.title("🤖 YouTube Shorts Script Generation Workflow")
st.markdown("This application uses the OpenAI API to execute a three-step script generation process.")

# --- Sidebar for API Key ---
with st.sidebar:
    st.header("Configuration")
    api_key_input = st.text_input("Enter your OpenAI API Key", type="password")
    st.markdown("[Get your API key here](https://platform.openai.com/account/api-keys)")

# --- Initialize Session State ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'key_patterns' not in st.session_state:
    st.session_state.key_patterns = ""
if 'video_ideas_raw' not in st.session_state:
    st.session_state.video_ideas_raw = ""
if 'final_scripts' not in st.session_state:
    st.session_state.final_scripts = ""
if 'parsed_ideas' not in st.session_state:
    st.session_state.parsed_ideas = []
if 'selected_idea_index' not in st.session_state:
    st.session_state.selected_idea_index = 0

# --- Step 1: Creative Analysis ---
st.header("Step 1: Analyze Video Transcripts")
with st.expander("Upload Transcripts and Analyze", expanded=st.session_state.step == 1):
    uploaded_files = st.file_uploader("Upload up to 3 video transcript files (.txt)", type=['txt'], accept_multiple_files=True)
    if st.button("Run Analysis (Step 1)"):
        if not api_key_input:
            st.warning("Please enter your OpenAI API Key in the sidebar.")
        elif uploaded_files:
            transcripts = [file.getvalue().decode("utf-8") for file in uploaded_files]
            prompt = get_prompt_1(transcripts)
            with st.spinner("Calling AI to analyze transcripts..."):
                st.session_state.key_patterns = call_chatgpt(api_key_input, prompt)
                st.session_state.step = 2
            st.success("Analysis Complete!")
            st.rerun()
        else:
            st.warning("Please upload at least one text file.")

if st.session_state.key_patterns:
    st.subheader("✅ AI-Generated Key Success Patterns")
    st.markdown(st.session_state.key_patterns)
    st.divider()

# --- Step 2: Strategic Ideation (COMPLETELY REVISED) ---
if st.session_state.step >= 2:
    st.header("Step 2: Define Campaign and Generate Ideas")
    with st.expander("Select a Campaign to Ideate", expanded=st.session_state.step == 2):
        
        # Create a list of names for the dropdown
        segment_names = [s['name'] for s in segments]
        selected_segment_name = st.selectbox(
            "Choose a target customer segment:",
            segment_names
        )

        # Find the full dictionary for the selected segment
        selected_segment = next((s for s in segments if s['name'] == selected_segment_name), None)

        # Display the details of the selected segment for confirmation
        if selected_segment:
            st.info("The following details will be used to generate ideas:")
            st.markdown(f"**Target Audience:**\n{selected_segment['audience']}")
            st.markdown(f"**Core Needs / Pain Points:**\n{selected_segment['pain_points']}")

        if st.button("Generate Ideas (Step 2)"):
            if not api_key_input:
                st.warning("Please enter your OpenAI API Key in the sidebar.")
            elif selected_segment:
                # Use the audience and pain_points from the selected segment dictionary
                audience_text = selected_segment['audience']
                pain_points_text = selected_segment['pain_points']
                
                prompt = get_prompt_2(st.session_state.key_patterns, audience_text, pain_points_text)
                with st.spinner("Calling AI to generate creative concepts..."):
                    raw_response = call_chatgpt(api_key_input, prompt)
                    st.session_state.video_ideas_raw = raw_response
                    st.session_state.parsed_ideas = parse_ideas(raw_response)
                    st.session_state.step = 3
                st.success(f"{len(st.session_state.parsed_ideas)} Video Ideas Generated and Parsed!")
                st.rerun()

if st.session_state.parsed_ideas:
    st.subheader("💡 AI-Generated Video Concepts")
    for i, idea in enumerate(st.session_state.parsed_ideas):
        with st.expander(f"**Concept {i+1}: {idea['title']}**"):
            st.markdown(f"**Core Message:** {idea['message']}")
            st.markdown(f"**Synopsis:** {idea['synopsis']}")
            st.markdown(f"**Strategic Alignment:** {idea['alignment']}")
    st.divider()

# --- Step 3: Script Generation ---
if st.session_state.step >= 3 and st.session_state.parsed_ideas:
    st.header("Step 3: Select and Refine Idea to Generate Scripts")
    with st.expander("Choose a Concept to Finalize Scripts", expanded=st.session_state.step == 3):
        
        idea_titles = [idea['title'] for idea in st.session_state.parsed_ideas]
        
        def on_dropdown_change():
            st.session_state.selected_idea_index = idea_titles.index(st.session_state.idea_selector)

        selected_title = st.selectbox(
            "Choose a video concept:",
            options=idea_titles,
            index=st.session_state.selected_idea_index,
            key='idea_selector',
            on_change=on_dropdown_change
        )
        
        selected_idea = st.session_state.parsed_ideas[st.session_state.selected_idea_index]

        st.subheader("Refine Concept Details (Editable)")
        final_title = st.text_input("Concept Title", value=selected_idea['title'])
        final_message = st.text_input("Core Message", value=selected_idea['message'])
        final_synopsis = st.text_area("Synopsis", value=selected_idea['synopsis'])
        
        st.info("The 'Strategic Alignment' is shown for context but not sent in the script prompt.")
        st.text_area("Strategic Alignment (for context)", value=selected_idea['alignment'], disabled=True)

        if st.button("Generate Japanese Scripts (Step 3)"):
            if not api_key_input:
                st.warning("Please enter your OpenAI API Key in the sidebar.")
            else:
                final_idea_for_prompt = {
                    "title": final_title,
                    "message": final_message,
                    "synopsis": final_synopsis
                }
                st.session_state.final_script_title = final_title
                prompt = get_prompt_3(final_idea_for_prompt)
                with st.spinner("Calling AI to write 3 distinct scripts in Japanese..."):
                    st.session_state.final_scripts = call_chatgpt(api_key_input, prompt)
                    st.session_state.step = 4
                st.success("Scripts are ready!")
                st.rerun()

if st.session_state.final_scripts:
    st.subheader(f"✍️ AI-Generated Japanese Scripts for '{st.session_state.get('final_script_title', '')}'")
    st.markdown(st.session_state.final_scripts)