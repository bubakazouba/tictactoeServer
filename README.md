##Current Goal:
* get it working

##GOALS:
```
* take into account disconnections
* resume online game(fow now the server will assume that every user has only one game and the client would expect the same, so if there is a game being resumed just ask the server if it has something for u and the server will send it)
* multiple games
* authentication
* uniquiness of username
* play again
* * make sure it's his turn before sending to other player(so we can prevent hacks, a player can play twice in a row if we dont do that)
```
---
ser.py listens on port 5005 (current ip: 104.236.133.238)
waits for either
>`{"username":username}` -->replies back--> `{"gameId":gameId,"playerId":playerId}`
>
>or
>
>`{"gameId":gameId,"playerId":playerId,"position":position}` -->sends to other player --> `{"position":position}`