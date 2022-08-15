# Container hosting SSH setup handler

Recieve a POST request public key and append to authorized_keys file.

Main project: https://github.com/KarmaComputing/container-hosting

## Test
```
curl http://127.0.0.1:5000 -H 'Content-Type: application/json' -d '{"CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY": "secret", "public_key": "ssh-rsa AAAAB3Nza..."}'
```
