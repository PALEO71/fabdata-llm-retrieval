# How to Install the scirag System
### Step-by-step guide — written for anyone, any age

---

## Before you start — what is this thing?

Think of this system as a **personal library assistant** that lives on your computer.
You feed it your own writing and research notes. It learns the connections between
ideas. When you need to write something, you ask it — and it finds the right pieces
for you, already in your voice.

It has three main parts:
- **A database** (a single file called `scirag.db`) — where everything is stored
- **An MCP server** — a small program that lets Claude talk to that database
- **Scripts** — tools you run once to feed your writing into the database

---

## Part 0 — What you need to install first (do this once, ever)

---

### Step 1 — Install Python

Python is the programming language this system is written in. Think of it as the engine.

1. Open your browser and go to **python.org/downloads**
2. Click the big yellow **"Download Python 3.12"** button
3. Run the installer
4. **IMPORTANT:** On the first screen, tick the box that says **"Add Python to PATH"**
   before clicking Install

To check it worked, open a terminal (see Step 2) and type:
```
python --version
```
You should see something like `Python 3.12.3`. If you do, you're good.

---

### Step 2 — Open a terminal

A terminal is a text window where you type commands. Think of it as talking directly
to your computer.

**On Windows:**
- Press the `Windows` key, type `cmd`, press Enter
- Or press `Windows + R`, type `cmd`, press Enter

**On Mac:**
- Press `Command + Space`, type `Terminal`, press Enter

You'll see a blinking cursor. That's where you type commands.

---

### Step 3 — Install uv (the package manager)

`uv` is like an app store for Python tools. It installs everything the project needs.

**On Windows**, paste this into your terminal and press Enter:
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**On Mac/Linux**, paste this:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

To check it worked:
```
uv --version
```
You should see a version number like `uv 0.5.1`.

---

### Step 4 — Install Git

Git is a tool that tracks changes to files, like a time machine for code.

1. Go to **git-scm.com/downloads**
2. Download the installer for your system
3. Run it — the default options are fine, just keep clicking Next

To check it worked:
```
git --version
```
You should see something like `git version 2.45.0`.

---

## Part 1 — Get the project onto your computer

---

### Step 5 — Download the project

In your terminal, navigate to a folder where you want to keep the project.
For example, to put it on your Desktop:

**On Windows:**
```
cd C:\Users\hvieira\Desktop
```

**On Mac:**
```
cd ~/Desktop
```

Then download the project:
```
git clone https://github.com/PALEO71/fabdata-llm-retrieval.git
```

This copies the project folder to your computer. You should see a new folder
called `fabdata-llm-retrieval` appear.

Now go into that folder:
```
cd fabdata-llm-retrieval
```

---

### Step 6 — Switch to the right branch

The project has different versions (called "branches"). We want the one with the
new system:

```
git checkout claude/portuguese-science-rag-w6DHw
```

You should see: `Switched to branch 'claude/portuguese-science-rag-w6DHw'`

---

### Step 7 — Install all the Python packages

The project needs several helper packages — like plug-ins. `uv` installs them all:

```
uv sync
```

This might take a minute. You'll see a list of packages being downloaded.
When it's done, you're ready for the next part.

---

## Part 2 — Set up your secret keys

---

### Step 8 — What are API keys?

API keys are like passwords that prove to external services (OpenAI, Anthropic)
that you have a paid account. Without them, the system can't create embeddings
(the "understanding" layer) or run connection agents.

You need two keys:
- **OpenAI API key** — for creating embeddings (the knowledge fingerprints)
- **Anthropic API key** — for the 17 connection agents

---

### Step 9 — Get your OpenAI key

1. Go to **platform.openai.com**
2. Log in or create an account
3. Click your profile icon → **"API keys"**
4. Click **"Create new secret key"**
5. Copy the key — it starts with `sk-`
6. **Save it somewhere safe.** You can only see it once.

---

### Step 10 — Get your Anthropic key

1. Go to **console.anthropic.com**
2. Log in or create an account
3. Click **"API Keys"** in the left menu
4. Click **"Create Key"**
5. Copy the key — it starts with `sk-ant-`
6. **Save it somewhere safe.**

---

### Step 11 — Create your `.env` file

A `.env` file is a hidden file where you store your secret keys. The project reads
it automatically. Think of it as a keychain that stays on your computer.

In your project folder, create a file called `.env`:

**On Windows**, type this in your terminal:
```
copy NUL .env
notepad .env
```

**On Mac:**
```
touch .env
open -e .env
```

In the file that opens, paste this — replacing the placeholder text with your
actual keys:

```
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

Save and close the file.

---

## Part 3 — Set up the database

---

### Step 12 — Create the database

This creates the `scirag.db` file and sets up all the tables inside it:

```
uv run python scripts/init_db.py
```

You should see: `Database initialised at scirag.db`

The database file is created in your project folder. It's just one file —
you can back it up by copying it like any other file.

---

## Part 4 — Feed your writing into the system

This is the most important part. You feed your writing in four rounds, from
most personal to most formal. Do **not** do them all at once — the order matters.

---

### Step 13 — Tier 1: Your published voice (do this first)

Put your Sul Informação columns and other published science communication pieces
into a folder. For example: `C:\Users\hvieira\second-brain\sources\divulgacao\`

Then run:
```
uv run python scripts/run_ingest.py --tier 1 --folder "C:\Users\hvieira\second-brain\sources\divulgacao"
```

This chops your articles into small pieces (called "chunks"), gives each piece
a fingerprint (called an "embedding"), and stores them in the database.

You should see a progress bar as each file is processed.

---

### Step 14 — Tier 2: Your field notes and research

Put your field notes and paleontology material in a folder:
`C:\Users\hvieira\second-brain\sources\investigacao\`

```
uv run python scripts/run_ingest.py --tier 2 --folder "C:\Users\hvieira\second-brain\sources\investigacao"
```

---

### Step 15 — Tier 3: Your teaching materials

Put workshop notes, slides, and classroom scripts in:
`C:\Users\hvieira\second-brain\sources\pedagogico\`

```
uv run python scripts/run_ingest.py --tier 3 --folder "C:\Users\hvieira\second-brain\sources\pedagogico"
```

---

### Step 16 — Tier 4: Formal papers and reports (optional)

Put formal academic papers you wrote (not ones you read — those go in the 2nd Brain):

```
uv run python scripts/run_ingest.py --tier 4 --folder "C:\Users\hvieira\second-brain\sources\institucional"
```

---

## Part 5 — Build the connections between ideas

---

### Step 17 — Run the connection agents

This is the clever part. 17 small AI agents read pairs of your writing pieces and
ask: "do these two ideas connect?" If yes, they write down *why*.

Run them in groups (each group takes a few minutes):

```
uv run python scripts/run_connections.py --group topical
uv run python scripts/run_connections.py --group bridges
uv run python scripts/run_connections.py --group place
uv run python scripts/run_connections.py --group voice_form
uv run python scripts/run_connections.py --group temporal
uv run python scripts/run_connections.py --group pedagogical
uv run python scripts/run_connections.py --group bilingual
```

Or run all 17 at once (takes longer):
```
uv run python scripts/run_connections.py --all
```

---

### Step 18 — Compile the wiki

This builds 8 thematic summary pages from all the connections just found.
Think of it as the system writing a mini-encyclopedia of your own knowledge:

```
uv run python scripts/run_wiki.py --all
```

---

## Part 6 — Connect to Claude Desktop

---

### Step 19 — Start the MCP server

The MCP server is the bridge between Claude Desktop and your database.
You need to leave this running while you use Claude Desktop.

```
uv run python -m scirag.mcp.server
```

You should see: `scirag MCP server running on port 8765`

Leave this terminal window open.

---

### Step 20 — Add the server to Claude Desktop

1. Open **Claude Desktop**
2. Go to **Settings** (the gear icon)
3. Click **"Developer"** → **"Edit Config"**
4. Add this block to the `mcpServers` section:

```json
{
  "mcpServers": {
    "scirag": {
      "command": "uv",
      "args": ["run", "python", "-m", "scirag.mcp.server"],
      "cwd": "C:\\Users\\hvieira\\Desktop\\fabdata-llm-retrieval"
    }
  }
}
```

Make sure the `cwd` path points to wherever you put the project folder.

5. Save the file and **restart Claude Desktop**

---

### Step 21 — Add SCIRAG.md to your Claude Desktop project

1. In Claude Desktop, open your project (the one with the 2nd Brain)
2. Go to project settings
3. Upload `SCIRAG.md` from the project folder as a reference file
   (or paste its contents into the project instructions)

This tells Claude how the scirag system works and how it connects to your 2nd Brain.

---

## Part 7 — Test that everything works

---

### Step 22 — Do a quick test

In Claude Desktop, try asking:

> "Search my corpus for anything about Algarve geology and give me a Sul Informação
> style opening paragraph."

If the system is working, Claude will:
1. Use the `search` tool to find relevant nodes
2. Use the `voice_match` tool to calibrate the register
3. Write a draft in your divulgação voice

---

## Updating the system over time

### When you write something new

Drop the new file into the appropriate sources folder, then run:
```
uv run python scripts/run_ingest.py --tier 1 --folder "path\to\folder"
uv run python scripts/run_connections.py --all
uv run python scripts/run_wiki.py --all
```

### When you want to rebuild a single wiki page

```
uv run python scripts/run_wiki.py --theme paleontologia_algarve
```

### To back up the database

Just copy `scirag.db` anywhere you like. It's one file. Done.

---

## If something goes wrong

| Problem | What to try |
|---|---|
| `python: command not found` | Go back to Step 1 and tick "Add Python to PATH" |
| `uv: command not found` | Close and reopen the terminal after Step 3 |
| `OPENAI_API_KEY not found` | Check your `.env` file has no extra spaces around the `=` |
| `Database not found` | Run Step 12 again |
| Claude Desktop doesn't see the tools | Make sure the terminal from Step 19 is still open |
| A script crashes mid-way | It's safe to re-run — the system skips already-processed files |

---

## Quick reference — the commands you'll use most

```bash
# Start the MCP server (do this first, every session)
uv run python -m scirag.mcp.server

# Add new writing (replace --tier and --folder as needed)
uv run python scripts/run_ingest.py --tier 1 --folder "path\to\folder"

# Rebuild all connections
uv run python scripts/run_connections.py --all

# Rebuild all wiki pages
uv run python scripts/run_wiki.py --all

# Rebuild one wiki page
uv run python scripts/run_wiki.py --theme paleontologia_algarve
```

---

*Total setup time: about 30 minutes the first time. After that, adding new writing
takes less than 5 minutes.*
