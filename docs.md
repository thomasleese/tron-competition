# Tron Competition

## Maths

All maths is integer based.

## Communication

Clients communicate with the server using TCP on port 4567. It is a UTF-8 based protocol.

### Handshake

When your client first connects to the server, you should send your name and colour.

	COLOUR r g b
	NAME name

Your name should not contain spaces.

### Arena Size

When the size of the arena changes (or when you connect) the server sends:

	ARENA width height

### Bikes

Every tick the server starts by sending you a list of all the bikes in the game.

	BIKE name x y r g b
	DEAD name

The server will then send a message letting you know you can now take your turn.

	G

At this point, you can take your turn.

### Your turn

To turn left, you send:

	L

To turn right, you send:
	
	R

To accelerate, you send:

	A

To deccelerate, you send:

	D

To do nothing, you send:

	N

To send a chat message (equivalent to doing nothing), you send:

	CHAT message

The server will then send to every client:

	CHAT name message

### Resetting

When someone connects, or when the game is over, the server sends a reset
message:

	RESET

## Sudden Death

After 5 minutes, the server activates sudden death mode. This means that your
bike will slowly continue accelerating until the game is over.
