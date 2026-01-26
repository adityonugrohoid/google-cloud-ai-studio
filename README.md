# Google Cloud AI Studio (Streamlit Edition)

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Live Deployed](https://img.shields.io/badge/status-live--deployed-brightgreen.svg)

A Python-based Streamlit application showcasing advanced AI-driven architectural design workflows powered by Google Vertex AI. This project demonstrates end-to-end GenAI application development on Google Cloud.

**Deployed on Google Cloud Run**: [https://google-cloud-ai-studio-1099058340933.us-central1.run.app](https://google-cloud-ai-studio-1099058340933.us-central1.run.app)

## 🎯 Project Goals
- **Advanced GenAI Workflow**: Implement a multi-step generation pipeline (Text -> Sketch -> Render).
- **Cloud Native**: Built specifically for Google Cloud Run with Vertex AI integration.
- **Production (Live/Deployed)**: A functional demonstration of advanced GenAI orchestration within the Google Cloud ecosystem, deployed and accessible at the live URL.

## 🌊 Workflow
1.  **Text Enhancement**: `gemini-2.0-flash-lite` expands simple descriptions.
2.  **Sketch Generation**: `gemini-2.5-flash-image` creates architectural line drawings.
3.  **Photorealistic Rendering**: `gemini-2.5-flash-image` transforms sketches into V-Ray style renders.

## 🛠️ Tech Stack
-   **Frontend**: Streamlit
-   **AI SDK**: Google Gen AI SDK (`google-genai`)
-   **Container**: Docker (Debian Slim)
-   **Deployment**: Google Cloud Run

## 🚀 Local Development

1.  **Clone & Navigate**
    ```bash
    cd google-cloud-ai-studio
    ```

2.  **Install Dependencies**
    Using [uv](https://github.com/astral-sh/uv):
    ```bash
    uv sync
    ```

3.  **Configuration**
    Set up your Google Cloud credentials.

    **Linux / Mac (Bash):**
    ```bash
    export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
    export GOOGLE_CLOUD_REGION="us-central1"
    gcloud auth application-default login

    # Verify configuration
    echo "Project: $GOOGLE_CLOUD_PROJECT"
    echo "Region: $GOOGLE_CLOUD_REGION"
    ```

    **Windows (PowerShell):**
    ```powershell
    $env:GOOGLE_CLOUD_PROJECT = $(gcloud config get-value project)
    $env:GOOGLE_CLOUD_REGION = "us-central1"
    gcloud auth application-default login

    # Verify configuration
    echo "Project: $env:GOOGLE_CLOUD_PROJECT"
    echo "Region: $env:GOOGLE_CLOUD_REGION"
    ```

4.  **Run Application**
    ```bash
    uv run streamlit run app.py
    ```

## ☁️ Cloud Run Deployment

1.  **Build**
    
    **Linux / Mac (Bash):**
    ```bash
    gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio
    ```

    **Windows (PowerShell):**
    ```powershell
    gcloud builds submit --tag gcr.io/$env:GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio
    ```

2.  **Deploy**

    **Linux / Mac (Bash):**
    ```bash
    gcloud run deploy google-cloud-ai-studio \
      --image gcr.io/$GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio \
      --platform managed \
      --allow-unauthenticated \
      --region $GOOGLE_CLOUD_REGION
    ```

    **Windows (PowerShell):**
    ```powershell
    gcloud run deploy google-cloud-ai-studio `
      --image gcr.io/$env:GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio `
      --platform managed `
      --allow-unauthenticated `
      --region $env:GOOGLE_CLOUD_REGION
    ```

3.  **One-Liner (Alternative - if env vars are already set)**

    **Windows (PowerShell):**
    ```powershell
    gcloud builds submit --tag gcr.io/$env:GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio && gcloud run deploy google-cloud-ai-studio --image gcr.io/$env:GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio --platform managed --allow-unauthenticated --region $env:GOOGLE_CLOUD_REGION
    ```

    **Linux / Mac (Bash):**
    ```bash
    gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio && gcloud run deploy google-cloud-ai-studio --image gcr.io/$GOOGLE_CLOUD_PROJECT/google-cloud-ai-studio --platform managed --allow-unauthenticated --region $GOOGLE_CLOUD_REGION
    ```

## 🧩 Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | - |
| `GOOGLE_CLOUD_REGION` | Vertex AI Region | us-central1 |
| `MODEL_TEXT` | Model for text enhancement | gemini-2.0-flash-lite |
| `MODEL_IMAGE` | Model for image generation | gemini-2.5-flash-image |

## Notable Code

This repository demonstrates cloud-native GenAI application patterns. See [NOTABLE_CODE.md](NOTABLE_CODE.md) for detailed code examples highlighting:

- Multi-step GenAI pipeline orchestration
- Cloud Run deployment configuration
- Vertex AI integration with modern SDK

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Adityo Nugroho**  
- Portfolio: https://adityonugrohoid.github.io  
- GitHub: https://github.com/adityonugrohoid  
- LinkedIn: https://www.linkedin.com/in/adityonugrohoid/

## 📈 Repository Stats
   
   ![Traffic Stats](./traffic-stats.svg)