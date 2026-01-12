import os
import streamlit as st
import base64
from PIL import Image
import io
from google import genai
from google.genai.types import GenerateContentConfig, Part

# Configure page


# Constants
MODEL_STEP1 = "gemini-2.0-flash-lite"
MODEL_STEP2 = "gemini-2.5-flash-image" 
MODEL_TEXT = os.environ.get("MODEL_TEXT", "gemini-2.0-flash-lite")
MODEL_IMAGE = os.environ.get("MODEL_IMAGE", "gemini-2.5-flash-image") 

# Setup Client
# Logic: Strictly use Vertex AI (Cloud Run with ADC or local gcloud auth)
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

try:
    client = genai.Client(vertexai=True, project=project_id, location=location)
    # client = None # Force failure for testing
except Exception as e:
    client = None

def step1_enhance_prompt(base_prompt):
    if not client: return None
    
    prompt = (
        'Expand this room description into 1-2 short sentences with key details. Be very brief (under 20 words).\n\n' +
        f'Room: {base_prompt[:200]}' # Truncate
    )
    
    try:
        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt,
            config=GenerateContentConfig(
                max_output_tokens=50,
                temperature=0.7
            )
        )
        return response.text.strip()
    except Exception as e:
        st.error(f"Step 1 Error: {e}")
        return None

def step2_generate_sketch(enhanced_prompt):
    if not client: return None
    
    sketch_prompt = (
        'Create a clean black-and-white architectural line drawing sketch. ' +
        'Pure black lines on white background. No shading, no color, no grayscale. ' +
        'Show perspective, layout, and all furniture/objects clearly.\n\n' +
        f'Room: {enhanced_prompt}'
    )
    
    try:
        response = client.models.generate_content(
            model=MODEL_IMAGE,
            contents=sketch_prompt,
        )
                
        # Iterate parts to find image
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data # Base64 bytes
                    
        return None
    except Exception as e:
        import traceback
        st.error(f"Step 2 Error: {e}")
        print(f"DEBUG STEP 2 ERROR: {e}")
        traceback.print_exc()
        return None

def step3_generate_render(sketch_bytes):
    if not client: return None
    
    render_prompt = (
        'Transform this into a high-end 3D render. ' +
        'Style: photorealistic architectural visualization (archviz). ' +
        'Ultra-high resolution textures, ray-traced lighting, soft shadows, volumetric light, ' +
        'realistic reflections, micro-surface details, natural color grading, and lens effects.'
    )
    
    # Construct Multimodal Content
    try:
        image_part = Part(
            inline_data={
                "data": sketch_bytes,
                "mime_type": "image/png"
            }
        )
        
        response = client.models.generate_content(
            model=MODEL_IMAGE,
            contents=[render_prompt, image_part],
            config=GenerateContentConfig(
                temperature=0.0,
                top_p=1.0,
                top_k=40
            )
        )
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data
        return None
    except Exception as e:
        st.error(f"Step 3 Error: {e}")
        return None


# UI Layout
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 AI Studio")

# Subtitle
st.markdown("*Generative Interior Design Workflow using Google Gemini*")

# Connection Status Indicator (Below Subtitle)
status_color = "#00e676" if client else "#ff1744" # Neon Green / Red
status_text = "System Online" if client else "System Offline"

st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px; margin-bottom: 20px;">
        <div style="
            height: 8px; 
            width: 8px; 
            background-color: {status_color}; 
            border-radius: 50%; 
            box-shadow: 0 0 8px {status_color};">
        </div>
        <span style="font-size: 0.8em; color: #808080; font-family: monospace;">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)
st.divider()

if not client:
    st.error("⚠️ Connection failed. Please check your Google Cloud credentials.")

# Input Form
st.subheader("📝 Design Preferences")

col1, col2 = st.columns(2)

with col1:
    room_type = st.selectbox(
        "Room Type",
        options=[
            "Living Room", "Bedroom", "Kitchen", "Bathroom", 
            "Dining Room", "Office", "Studio", "Balcony"
        ],
        index=0,
    )
    
    design_style = st.selectbox(
        "Style",
        options=[
            "Modern", "Minimalist", "Industrial", "Bohemian", 
            "Scandinavian", "Traditional", "Rustic", "Art Deco"
        ],
        index=0,
    )

with col2:
    material_focus = st.selectbox(
        "Main Material",
        options=[
            "Wood", "Marble", "Concrete", "Glass", 
            "Brick", "Metal", "Fabric", "Stone"
        ],
        index=0,
    )
    
    color_palette = st.selectbox(
        "Color Palette",
        options=[
            "Neutral", "Warm", "Cool", "Pastel", 
            "Dark & Moody", "Vibrant", "Earth Tones", "Monochrome"
        ],
        index=0,
    )

# Additional Details (Optional)
additional_details = st.text_input(
    "Additional Details (Optional)",
    placeholder="e.g., large windows, high ceiling, cozy atmosphere",
    help="Add specific requirements to refine the design"
)

# Construct Base Prompt
base_prompt = f"{design_style} {room_type} with focus on {material_focus} and {color_palette} tones. {additional_details}"

# Generate Button
st.divider()
generate_btn = st.button(
    "🚀 Generate Design",
    type="primary",
    use_container_width=True,
)

# Workflow Section
if generate_btn:
    st.subheader("✨ Generation Workflow")
    
    # Session State for storing steps
    if "step1_text" not in st.session_state: st.session_state.step1_text = ""
    if "step2_image" not in st.session_state: st.session_state.step2_image = None
    if "step3_image" not in st.session_state: st.session_state.step3_image = None

    # Step 1
    with st.status("Step 1: Enhancing Design Brief...", expanded=True) as status:
        st.session_state.step1_text = step1_enhance_prompt(base_prompt)
        if st.session_state.step1_text:
            st.write(f"**Enhanced Brief:** {st.session_state.step1_text}")
            status.update(label="Brief Enhanced!", state="complete", expanded=False)
        else:
            status.update(label="Step 1 Failed", state="error")
            st.stop()
    
    # Step 2
    with st.status("Step 2: Generating Architectural Sketch...", expanded=True) as status:
        st.session_state.step2_image = step2_generate_sketch(st.session_state.step1_text)
        if st.session_state.step2_image:
             # Convert to PIL for display
            img = Image.open(io.BytesIO(st.session_state.step2_image))
            st.image(img, caption="GenAI Sketch", width="stretch")
            status.update(label="Sketch Generated!", state="complete", expanded=False)
        else:
            status.update(label="Step 2 Failed", state="error")
            st.stop()

    # Step 3
    with st.status("Step 3: Rendering Photorealistic Image...", expanded=True) as status:
        st.session_state.step3_image = step3_generate_render(st.session_state.step2_image)
        if st.session_state.step3_image:
            img_final = Image.open(io.BytesIO(st.session_state.step3_image))
            st.image(img_final, caption="Final Render", width="stretch")
            status.update(label="Render Complete!", state="complete", expanded=False)
        else:
            status.update(label="Step 3 Failed", state="error")

# Footer
st.divider()
st.caption(
    "Built with [Streamlit](https://streamlit.io) and "
    "[Google Gemini](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) | "
    "Author: Adityo Nugroho"
)
