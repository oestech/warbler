# Before you start

Welcome. A few facts about this session so nothing is a surprise.

## This round is AI-enabled

You are expected to use **Claude Code**, the agentic CLI, as part of how you
work. It is installed and pre-authenticated — no API key, no login. To start:
open a terminal and type:

```
claude
```

How much or how little you lean on it is up to you; using it well is part of
what this round looks at.

## Permission mode

Claude Code is configured in **auto mode**: an automated reviewer checks each
action the agent wants to take before it runs. Most actions proceed without
interrupting you; occasionally you'll be asked to approve something. This is
identical for every candidate and can't be changed mid-session.

## The environment

- **Dependencies are pre-installed.** No setup needed. Run the tests any time
  with:

  ```
  python -m pytest
  ```

- **Connect via VS Code desktop or `gh codespace ssh`** rather than the browser
  tab — Claude Code is a terminal UI and browser terminals mangle keybindings
  and copy-paste.

## Ground rules

- You may ask the interviewer clarifying questions at any time, the same as you
  would a colleague.
- At the end you'll be asked to walk through the result and explain and defend
  the code — including the parts the model wrote.
- At the end the interviewer will also ask you to run one short script that
  saves the session record.

Good luck.
