FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sudo \
      lua5.4 \
      luarocks \
      build-essential \
      unzip \
      git \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*


COPY . .

RUN luarocks install busted
RUN luarocks install luacheck
RUN luarocks install lua-cjson

WORKDIR /app

# FROM ubuntu:22.04

# ENV DEBIAN_FRONTEND=noninteractive
# WORKDIR /app

# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#       ca-certificates \
#       curl \
#       git \
#       unzip \
#       sudo \
#       lua5.4 \
#       luarocks \
#       build-essential && \
#     rm -rf /var/lib/apt/lists/*

# # 2) Luau CLI (luau + luau-analyze) を導入
# #    - バージョン固定したい場合は LUAU_VERSION を pin
# ARG LUAU_VERSION=latest
# RUN set -eux; \
#     if [ "$LUAU_VERSION" = "latest" ]; then \
#         ZIP_URL=$(curl -fsSL https://api.github.com/repos/luau-lang/luau/releases/latest \
#           | grep -oE 'https://[^"]+/luau-ubuntu.zip'); \
#     else \
#         ZIP_URL="https://github.com/luau-lang/luau/releases/download/${LUAU_VERSION}/luau-ubuntu.zip"; \
#     fi; \
#     echo "Fetching: ${ZIP_URL}"; \
#     curl -fsSL "$ZIP_URL" -o /tmp/luau-ubuntu.zip; \
#     unzip -q /tmp/luau-ubuntu.zip -d /tmp/luau; \
#     install -m 0755 /tmp/luau/luau /usr/local/bin/luau; \
#     install -m 0755 /tmp/luau/luau-analyze /usr/local/bin/luau-analyze; \
#     rm -rf /tmp/luau /tmp/luau-ubuntu.zip

# RUN luarocks install busted && \
#     luarocks install luacheck

# COPY . .

# WORKDIR /app