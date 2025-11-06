import streamlit as st
from src.aislides.core.generator.generator import generate_presentation
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.core.engines.tex.generator import generate_tex_and_pdf
from src.aislides.core.iterator.iterator import regenerate_slide
import os

# --- Session state to mirror CLI variables ---
if "original_prompt" not in st.session_state:
    st.session_state.original_prompt = ""
if "res" not in st.session_state:
    st.session_state.res = None
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "mode" not in st.session_state:
    st.session_state.mode = "main"  # "main" or "edit_slide"

st.title("AI Slide Generator")

# --- Step 1: Get original topic (once) ---
if not st.session_state.original_prompt:
    topic = st.text_input("Enter a topic for the presentation:")
    if st.button("🚀 Set Topic"):
        if topic.strip():
            st.session_state.original_prompt = topic.strip()
            st.rerun()
    st.stop()

st.write(f"**Topic:** {st.session_state.original_prompt}")

# --- Main mode: generate or refine full presentation ---
if st.session_state.mode == "main":
    refine_prompt = st.text_input(
        "Enter your slide gen prompt if you want to refine it (or leave as is):",
        value=st.session_state.original_prompt
    )
    current_prompt = refine_prompt.strip() or st.session_state.original_prompt

    st.write("Select output format to generate:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate PPTX"):
            res = generate_presentation(current_prompt, st.session_state.original_prompt)
            structure_to_ppt(res, save_path="test.pptx")
            st.session_state.res = res
            st.session_state.pdf_path = None # Clear pdf path
            st.rerun()
    with col2:
        if st.button("Generate PDF"):
            pdf_path = generate_tex_and_pdf(current_prompt, st.session_state.original_prompt)
            st.session_state.pdf_path = pdf_path
            st.session_state.res = None # Clear res
            st.rerun()

    if st.session_state.res:
        st.success("PPTX generated successfully!")
        if st.button("✏️ Edit a Slide"):
            st.session_state.mode = "edit_slide"
            st.rerun()

    if st.session_state.pdf_path:
        st.success("PDF generated successfully!")
        with open(st.session_state.pdf_path, "rb") as f:
            pdf_bytes = f.read()
            st.pdf(pdf_bytes, height=700)  # Displays PDF inline in Streamlit

        st.download_button(
            "⬇️ Download PDF", 
            pdf_bytes, 
            file_name=os.path.basename(st.session_state.pdf_path)
        )



# --- Edit slide mode ---
elif st.session_state.mode == "edit_slide":
    res = st.session_state.res
    if not res:
        st.session_state.mode = "main"
        st.rerun()

    slide_count = len(res.slides)
    slide_choice = st.selectbox(
        "Enter the slide number you wish to change:",
        options=list(range(1, slide_count + 1)),
        format_func=lambda x: f"Slide {x}"
    )
    new_content = st.text_input(f"Enter new content prompt for slide {slide_choice}:")

    if st.button("🔄 Update Slide"):
        edited_ppt = regenerate_slide(
            presentation=res,
            slide_index=slide_choice - 1,
            edit_prompt=new_content,
            original_prompt=st.session_state.original_prompt,
        )
        structure_to_ppt(edited_ppt, save_path="test.pptx")
        st.session_state.res = edited_ppt
        st.rerun()

    if st.button("⬅️ Back"):
        st.session_state.mode = "main"
        st.rerun()