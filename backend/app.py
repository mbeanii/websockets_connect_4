#!/usr/bin/env python

import asyncio
import websockets
import json
from connect4 import PLAYER1, PLAYER2, Connect4


player = PLAYER1


class InvalidPlayerError(BaseException):
    pass


def swap_player():
    global player
    if player == PLAYER1:
        player = PLAYER2
    elif player == PLAYER2:
        player = PLAYER1
    else:
        raise InvalidPlayerError()


async def handler(websocket):
    global player
    # Initialize a Connect Four game.
    game = Connect4()
    async for message in websocket:
        print(message)
        message = json.loads(message)
        if message["type"] != "play":
            raise Exception(f"Invalid message type: {message['type']}")
        try:
            column = message["column"]
            row = game.play(player, column)
            swap_player()
            print(row)
        except RuntimeError as e:
            send_message = {
                "type": "error",
                "message": repr(e)
            }
            await websocket.send(json.dumps(send_message))
            break
        send_message = {
            "type": "play",
            "player": game.last_player,
            "column": column,
            "row": row
        }
        await websocket.send(json.dumps(send_message))
        # if the move won the game, send an event of type "win"
        if game.last_player_won:
            send_message = {
                "type": "win",
                "player": game.last_player
            }
            await websocket.send(json.dumps(send_message))
            player = PLAYER1


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
