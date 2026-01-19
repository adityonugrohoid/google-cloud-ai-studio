# Notable Code: Google Cloud AI Studio

**Production Readiness Level:** Live Prod

This document highlights key code sections that demonstrate the technical strengths and architectural patterns implemented in this cloud-native GenAI application.

## Overview

Google Cloud AI Studio is a cloud-native Streamlit application demonstrating advanced GenAI workflow orchestration using Google Vertex AI. The system implements a multi-step generation pipeline that transforms simple text descriptions into photorealistic architectural renders through three stages.

---

## 1. Multi-Step GenAI Pipeline

**File:** `app.py`  
**Lines:** 29-117

The three-stage pipeline demonstrates clean orchestration of multiple AI models in sequence.

```python
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
        st.error(f"Step 2 Error: {e}")
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
```

**Why it's notable:**
- Clear separation of three pipeline stages
- Sequential data flow: text → enhanced text → sketch → render
- Proper error handling at each stage
- Multimodal content handling (text + image inputs)
- Uses modern `google-genai` SDK with proper configuration

---

## 2. Cloud Run Deployment Configuration

**File:** `Dockerfile`  
**Lines:** 1-24

The Dockerfile demonstrates proper containerization for Cloud Run deployment.

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy application files
COPY pyproject.toml .
COPY app.py .

# Install dependencies
# Using --system to install into the system python environment (no venv needed in container)
RUN uv pip install --system .

# Expose the Streamlit port
EXPOSE 8080

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

**Why it's notable:**
- Optimized base image (python:3.12-slim)
- Uses `uv` for fast dependency installation
- Proper port configuration for Cloud Run (8080)
- Environment variables for Streamlit configuration
- Production-ready containerization

---

## 3. Vertex AI Client Initialization

**File:** `app.py`  
**Lines:** 18-27

The Vertex AI client setup demonstrates proper cloud authentication and configuration.

```python
# Setup Client
# Logic: Strictly use Vertex AI (Cloud Run with ADC or local gcloud auth)
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

try:
    client = genai.Client(vertexai=True, project=project_id, location=location)
except Exception as e:
    client = None
```

**Why it's notable:**
- Uses `vertexai=True` for Vertex AI (not generic API)
- Proper environment variable configuration
- Application Default Credentials (ADC) support
- Graceful error handling if client fails
- Region configuration for optimal latency

---

## 4. Sequential Pipeline Execution with State Management

**File:** `app.py`  
**Lines:** 218-257

The UI demonstrates proper state management for multi-step pipeline execution.

```python
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
```

**Why it's notable:**
- Proper session state management for pipeline steps
- Sequential execution with early termination on errors
- Visual progress indicators using `st.status`
- Image handling and display between steps
- Clean error handling with user feedback

---

## Architecture Highlights

### Multi-Step Pipeline

1. **Text Enhancement**: Gemini 2.0 Flash Lite expands descriptions
2. **Sketch Generation**: Gemini 2.5 Flash Image creates line drawings
3. **Photorealistic Rendering**: Gemini 2.5 Flash Image transforms sketches

### Cloud-Native Design

- Docker containerization
- Cloud Run deployment
- Vertex AI integration
- Environment-based configuration

---

## Technical Strengths Demonstrated

- **Multi-Model Orchestration**: Chains different AI models for complex workflows
- **Cloud Deployment**: Actually deployed and live on Cloud Run
- **Modern SDK**: Uses `google-genai` (not deprecated)
- **State Management**: Proper session state for multi-step workflows
- **Error Handling**: Graceful degradation at each pipeline stage
