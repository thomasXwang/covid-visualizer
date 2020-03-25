mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"20924993+Thomas2512@users.noreply.github.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\

[runner]
magicEnabled = false
" > ~/.streamlit/config.toml