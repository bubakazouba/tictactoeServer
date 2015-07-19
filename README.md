##Current Goal:
* 1I get it working

##GOALS:
```
* --------------------------------------------
* FIRST RELEASE:
* 1S make sure it's his turn before sending to other player(so we can prevent hacks, a player can play twice in a row if we dont do that)
* 2I/S uniquiness of username
*  -choose a username or play as guest (u cant resume online games/track scores/etc..)
*  
* 3S if ack doesnt go through 5 times, just disconnect
*
* 4S play against a specific user
 - specify username
 - generate a link and send it
 	- send through whatsapp/telegram/facebook/SMS

* 5I/S take into account disconnections
* 6S/Iplay again will be implemented in the following way:
 when the game ends, the client will

- send the game type to the server
- server has to make sure the two players playing are playing the same game type
- support the normal (3x3) game too (next release?)
* ------------------------------------------ 
* AI!!!
* voice recognition
* leaderboard
 - work on statistics in DB
*  
* resume online game(fow now the server will assume that every user has only one game and the client would expect the same, so if there is a game being resumed just ask the server if it has something for u and the server will send it)
* resume online game Version 2: when the game opens it sends the server it's username and asks it if has any plays waiting on this player,server sends any waiting plays for every game and client updates UI for all of them
* 
* multiple games (cancel games if no activiy for x days/let user set this in the settings)
* 
* authentication
* 
* in settings: volume
* 
* push notifications:
* 	if he didnt play for a long time push (come on $username is waiting for u)
*  idk what else
*  
*
* beat that game: https://play.google.com/store/apps/details?id=com.rts.android.tictactoe
```
---
ser.py listens on port 5005 (current ip: 104.236.133.238)
waits for either
>`{"username":username}` -->replies back--> `{"gameId":gameId,"playerId":playerId}`
>
>or
>
>`{"gameId":gameId,"playerId":playerId,"position":position}` -->sends to other player --> `{"position":position}`
