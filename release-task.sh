#!/bin/bash
set -e  # Stop the script on the first error
# Notify Keybase
curl -X POST --location "https://marvn.app/add_message" -H "Content-Type: application/json" -d '{"sender": "https://marvn.app ", "message": "@marvn Releasing", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTQzMzIxODcsInVzZXIiOiJwYXN0b3JodWRzb24iLCJjb252ZXJzYXRpb25faWQiOiIwMDAwYzNlMWRhZjI5NmU2Yzg5M2EwMmY2YWUyZTM5YmJlOTllY2ZiZGM3YmVjNmRhY2NiM2ZkOWVmYjAzODJkIn0.tTtUE0E583rqNUhtlOPbF7pYOxxQhnIt1Jc5PXzCSrk"}'
