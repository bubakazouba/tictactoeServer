##Current Goal:
* get it working

##GOALS:
```
* take into account disconnections
* play again
* make sure it's his turn before sending to other player(so we can prevent hacks, a player can play twice in a row if we dont do that)
* multiple games
* authentication
* uniquiness of username
```
---
ser.py listens on port 5005 (current ip: 104.236.133.238)
waits for either
>`{"username":username}` -->replies back--> `{"gameId":gameId,"playerId":playerId}`
>
>or
>
>`{"gameId":gameId,"playerId":playerId,"position":position}` -->sends to other player --> `{"position":position}`