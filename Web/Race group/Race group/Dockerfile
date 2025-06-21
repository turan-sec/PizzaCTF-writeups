# Use Node.js as base image
FROM node:18

# Install wkhtmltopdf
RUN curl -L https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz \
    -o wkhtmltox.tar.xz \
 && tar -xJf wkhtmltox.tar.xz -C /opt \
 && ln -s /opt/wkhtmltox/bin/wkhtmltopdf /usr/bin/wkhtmltopdf \
 && rm wkhtmltox.tar.xz

# Write flag file
RUN echo 'turan{0ops_u_g0t_the_flag}' > /root/flag.txt

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy all source files
COPY . .

# Expose app port (adjust if needed)
EXPOSE 3000

# Start the app
CMD ["node", "server.js"]
