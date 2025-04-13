1. Copy .env.example to .env
2. Add your Brawl Stars API key, you can generate your own key following [this documentation](https://developer.brawlstars.com/#/)
3. Install docker 
4. run docker compose up:
    ```bash
    docker compose up -d
    ```
5. execute the python script
    ```bash
    python get_brawlstars_data.py
    ```