FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    wget \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Setup Nginx and Supervisor
RUN apt-get update && apt-get install -y procps nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Setup user and permissions
RUN useradd -m as-user
RUN chown -R as-user:as-user /var/log /run /var/lib/nginx

# Setup workspace
RUN mkdir -p /action-server/datadir /action-server/actions
RUN chown -R as-user:as-user /action-server

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    libxkbcommon0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /action-server/actions

# Setup Action Server
RUN curl -o action-server https://cdn.sema4.ai/action-server/releases/latest/linux64/action-server && \
    chmod a+x  action-server && \
    mv action-server /usr/local/bin/

# Copy files first while still root
COPY . .

USER as-user

RUN action-server import --datadir=/action-server/datadir

EXPOSE 8080

CMD ["/usr/bin/supervisord"]