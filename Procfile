web: gunicorn webhook_bot:app
bot: python morethanmarvin.py
release: curl -X POST --location "https://marvn.app/add_message" -H "Content-Type: application/json" -d '{"message": "New Marvn Released", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTA3MzA5NzIsInVzZXIiOiJwYXN0b3JodWRzb24iLCJjb252ZXJzYXRpb25faWQiOiIwMDAwYzNlMWRhZjI5NmU2Yzg5M2EwMmY2YWUyZTM5YmJlOTllY2ZiZGM3YmVjNmRhY2NiM2ZkOWVmYjAzODJkIn0.uDI2cCpQ3PQQ7QgmzXpkuSPH3GQ_sb-Ku_j358y9PH0"}'