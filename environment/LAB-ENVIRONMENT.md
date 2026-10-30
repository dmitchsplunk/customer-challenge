# The workshop environment

What is already on each participant's EC2 workshop host, and what that means for
how you build, instrument, and show your agent. Read this with step 3 of the
README. You install Python 3.12 in step 3 and use it for the agent. You do
not install a model, create a Splunk project, or apply a laptop proxy fix.

## Variables on your host

The following environment variables will be automatically set on your EC2 workshop host. 
You can confirm which variables are set by running the following command: 

```bash
env | grep -oE '^(SPLUNK_AO|OPENAI)[A-Z_]*|^INSTANCE'
```

| Variable | What it is | What you do with it |
|---|---|---|
| `OPENAI_API_KEY` | Key for the OpenAI-compatible endpoint on this host. | If it is set, leave it set; the agent reads it from the environment. If it is empty, ask your facilitator. |
| `OPENAI_BASE_URL` | That endpoint. | The starter agents pass it as the client's base URL. |
| `SPLUNK_AO_CONSOLE_URL` | Agent Observability console for this instance. | Open this URL in a browser to see traces. |
| `SPLUNK_AO_API_URL` | API the `splunk-ao` SDK calls. | Leave it set. The SDK reads it. |
| `SPLUNK_AO_API_KEY` | Key the SDK uses to send traces. | Leave it set. Do not paste it into code. |
| `SPLUNK_AO_PROJECT` | Project on this instance. Traces go here. | Use this project. Do not create another one. |
| `INSTANCE` | Agent stream name for this host. | Your `.env` sets `SPLUNK_AO_AGENT_STREAM=${INSTANCE}`, so the SDK reads it. Or pass it as `agent_stream` when you create the logger. |
| `SPLUNK_AO_USER` | Console login. | Browser only. The SDK does not read it. |
| `SPLUNK_AO_PASSWORD` | Console login. | Browser only. The SDK does not read it. |
| `SPLUNK_AO_USER_ID` | Console login. | Browser only. The SDK does not read it. |

The model behind `OPENAI_BASE_URL` is `gpt-4.1-mini`. Do not change it. 

The SDK sends traces with `SPLUNK_AO_CONSOLE_URL`, `SPLUNK_AO_API_URL`,
`SPLUNK_AO_API_KEY`, and `SPLUNK_AO_PROJECT`. The agent stream is `INSTANCE`.
If you do not use the `.env` line that sets `SPLUNK_AO_AGENT_STREAM`, 
give it to the logger yourself:

```python
logger = SplunkAOLogger(
    project=os.environ["SPLUNK_AO_PROJECT"],
    agent_stream=os.environ["INSTANCE"],
)
```

Do not create another project or type a different stream name. A second project splits your traces.

Install the SDK into the agent's virtualenv when you instrument, not before:

```bash
pip install "splunk-ao[langchain]"   # LangGraph path
pip install splunk-ao                # pure-Python path
```

## Also on the host, not used

The image also carries a k3d Kubernetes cluster and Traefik ingress. The
challenge does not use them. Run the agent from the terminal. Traces go to
Splunk Agent Observability from there.

## Things that bite

- A model name other than `gpt-4.1-mini` (for example `gpt-4o-mini`) gets a 404 from the gateway.
- Copying a `.env` that sets `OPENAI_API_KEY=` or `OPENAI_BASE_URL=` to an empty value, then sourcing that file, wipes the host values. `python-dotenv` does not override variables that are already set, so `cp .env.example .env` is safe. Do not `export` the empty lines.
- `SPLUNK_AO_USER`, `SPLUNK_AO_PASSWORD`, and `SPLUNK_AO_USER_ID` log you into the console. Putting them in the agent does not route traces.
- Creating a second project, or hard-coding a different `SPLUNK_AO_PROJECT`, sends traces somewhere you will not be looking.
- The corporate proxy rules for a managed laptop do not apply on this host. Do not spend time on a TLS proxy bundle.
