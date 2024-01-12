#!/bin/bash
set -e  # Stop the script on the first error

# Notify Keybase
curl -X POST --location "https://marvn.app/add_message" -H "Content-Type: application/json" -d '{"message": "@marvn Releasing", "sender": "Dokku", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDUwMzQ0NjcsInVzZXIiOiJwYXN0b3JodWRzb24iLCJjb252ZXJzYXRpb25faWQiOiIwMDAwYzNlMWRhZjI5NmU2Yzg5M2EwMmY2YWUyZTM5YmJlOTllY2ZiZGM3YmVjNmRhY2NiM2ZkOWVmYjAzODJkIn0.vXs05VfuFlkD_p0K8bQo9GV5P87HLpgkpabL3eD3BcU"}'
