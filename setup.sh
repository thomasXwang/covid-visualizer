mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"250395@live.fr\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\

[runner]
magicEnabled = false
" > ~/.streamlit/config.toml