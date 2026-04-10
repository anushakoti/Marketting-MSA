# 🌿 EcoShop AI — Marketing Multi-Agent SaaS

> An AI-powered branding and strategy assistant for sustainable businesses, built with LangGraph multi-agent orchestration, AWS Bedrock image generation, Supabase authentication, and persistent chat history.

---

## 📖 Overview

EcoShop AI is a SaaS application that helps sustainable businesses build their brand identity from the ground up. Users can generate brand logos, craft SEO strategies, define brand voice, and more — all through a conversational AI interface powered by a LangGraph multi-agent system. Every session is saved, so users can pick up right where they left off.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Multi-user Authentication** | Secure sign-up and login via Supabase Auth |
| 💬 **Persistent Chat History** | Conversations saved to a database and resumable at any time |
| 🖼️ **AI Logo Generation** | Brand logos generated using Amazon Bedrock and stored in Supabase Storage |
| 📊 **Asset Dashboard** | Central view to browse, track, and download all generated brand assets |
| 🤖 **Multi-Agent Orchestration** | Intelligent agent routing via LangGraph for specialized branding tasks |
| 🌱 **Sustainability Focus** | Tailored strategies and messaging for eco-conscious businesses |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Frontend                  │
│         (Login / Chat / Dashboard pages)             │
└────────────────────┬────────────────────────────────┘
                     │
           ┌─────────▼──────────┐
           │   LangGraph Graph   │
           │  (graph/ module)    │
           └─────────┬──────────┘
                     │ routes to
        ┌────────────┼────────────┐
        ▼            ▼            ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │  Brand   │ │   SEO    │ │  Logo    │
  │ Strategy │ │  Agent   │ │Generator │  ... more agents
  │  Agent   │ │          │ │(Bedrock) │
  └──────────┘ └──────────┘ └──────────┘
                     │
           ┌─────────▼──────────┐
           │  Supabase Backend  │
           │  Auth / DB / Store │
           └────────────────────┘
```

---

## 📁 Project Structure

```
Marketing-MSA/
├── app.py                  # Main Streamlit multi-page application
├── cli.py                  # CLI interface for testing agents
├── supabase_client.py      # Supabase Auth, Database & Storage manager
├── requirements.txt        # Python dependencies
├── .gitignore
├── agents/                 # Individual AI agent tools
│   ├── logo_generator.py   # AWS Bedrock image generation agent
│   ├── seo_agent.py        # SEO strategy agent
│   └── ...                 # Other branding agents
└── graph/                  # LangGraph orchestration
    ├── state.py            # Agent state schema
    └── workflow.py         # Graph definition and routing logic
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [Supabase](https://supabase.com/) account (free tier works)
- [AWS account](https://aws.amazon.com/) with access to Amazon Bedrock

### 1. Clone the Repository

```bash
git clone https://github.com/anushakoti/Marketing-MSA.git
cd Marketing-MSA
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Supabase Credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
```

### 4. Set Up Supabase

#### Create Database Tables

In your Supabase project, navigate to the **SQL Editor** and run:

```sql
-- Conversations table
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT,
  content TEXT,
  extras JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Create Storage Bucket

1. Go to **Storage** in your Supabase dashboard.
2. Create a new bucket named **`assets`**.
3. Set its visibility to **Public**.
4. Add a policy allowing authenticated users to **INSERT** and **SELECT** objects.

---

## ▶️ Running the App

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

### Navigation

- **🏠 Home** — Overview of the AI assistant and its capabilities
- **🔑 Login / Signup** — Create an account or sign in
- **💬 Chatbot** — Start a branding conversation with the AI agents
- **📊 Dashboard** — View and download your saved logos and brand assets

### CLI Mode (for testing)

```bash
python cli.py
```

---

## 🤖 AI Agents

The multi-agent system uses **LangGraph** to intelligently route user requests to the appropriate specialist agent:

| Agent | Capability |
|---|---|
| **Brand Strategy Agent** | Defines brand mission, values, and positioning |
| **Logo Generator** | Creates visual logos using AWS Bedrock image models |
| **SEO Agent** | Generates keyword strategies and SEO-optimized content |
| *(additional agents)* | Further branding and marketing tools |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **Agent Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| **Image Generation** | [AWS Bedrock](https://aws.amazon.com/bedrock/) |
| **Auth & Database** | [Supabase](https://supabase.com/) (PostgreSQL) |
| **File Storage** | Supabase Storage |
| **Language** | Python 3.10+ |

---

## 🔒 Security Notes

- Never commit your `.env` file. It is already included in `.gitignore`.
- Use Supabase Row Level Security (RLS) policies to ensure users can only access their own conversations and assets.
- Rotate AWS credentials regularly and use least-privilege IAM roles.

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to your branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is open-source. Please add a `LICENSE` file if you intend to publish or distribute it.

---

## 👤 Author

**Anusha Koti** — [GitHub](https://github.com/anushakoti)
