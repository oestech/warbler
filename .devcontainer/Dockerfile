# Base image pinned by digest, not tag: tags move between weeks, digests don't.
# Digest resolved 2026-08-27 for mcr.microsoft.com/devcontainers/python:3.11-bookworm
FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm@sha256:ea38ccb07ef56e45e4c10494c2ac9518cf6ad4476f5a66796b44369a9d96abe2

ARG CLAUDE_CODE_VERSION=2.1.246

# Capture tooling. The base image already provides git, curl, sudo, and the
# non-root "vscode" user.
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Managed settings sit at the top of Claude Code's settings precedence chain,
# above ~/.claude and the project's .claude/. Installing from the image makes the
# posture enforced rather than suggested (tamper-evident: rebuilding is slow and
# visible, though not impossible).
COPY managed-settings.json /etc/claude-code/managed-settings.json

# Flush shell history to disk continuously so capture-session.sh sees the live
# session, not just exited shells.
RUN echo "export PROMPT_COMMAND='history -a'" >> /etc/bash.bashrc \
    && echo "setopt INC_APPEND_HISTORY" >> /etc/zsh/zshrc

# The CLI must never self-update: the pinned version is the reproducibility
# guarantee across the hiring loop.
ENV DISABLE_AUTOUPDATER=1
ENV DEVCONTAINER=true

# Native installer (no Node dependency on a Python image); installs an exact
# pinned version to ~/.local/bin.
USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash -s "${CLAUDE_CODE_VERSION}"
ENV PATH="/home/vscode/.local/bin:${PATH}"
