FROM nginx:1.27-alpine

# Serve the static frontend files (html/css/js) via nginx.
# The app entrypoint remains /html/index.html
COPY . /usr/share/nginx/html

# Make '/' serve our app (instead of nginx default welcome page).
COPY ./html/index.html /usr/share/nginx/html/index.html

# Provide a stable top-level route for the ski page.
COPY ./html/ski_index.html /usr/share/nginx/html/ski_index.html

# Generate /env.js from container env vars on startup.
COPY ./docker-entrypoint.d/99-env.sh /docker-entrypoint.d/99-env.sh
RUN chmod +x /docker-entrypoint.d/99-env.sh

EXPOSE 80
