import uvicorn

uvicorn.run("services.api.simulation_app:app", host="127.0.0.1", port=8000)
