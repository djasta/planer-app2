def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                return {}

        # AUTO FIX / MIGRACIJA STAROG FORMAT-a
        for month in list(data.keys()):
            if isinstance(data[month], list):
                data[month] = {
                    "plata": 0.0,
                    "troskovi": data[month]
                }

            if not isinstance(data[month], dict):
                data[month] = {
                    "plata": 0.0,
                    "troskovi": []
                }

        return data

    return {}
