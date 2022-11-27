from collections import defaultdict
from uuid import UUID

from app.api.context import WebSocketRequestContext
from app.common import logger
from app.common.errors import ServiceError
from app.models import ClientMessages
from app.models import Packet
from app.models import ServerMessages
from app.models.chat_messages import SendChatMessage
from app.usecases import chat_messages
from app.usecases import sessions
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi import WebSocketException

router = APIRouter()


# TODO: responses module

# TODO: track which hosts have which websockets in redis?
# that way this could be distributed (i suppose)
WEBSOCKETS: dict[int, list[WebSocket]] = defaultdict(list)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    ctx: WebSocketRequestContext = Depends(),
):
    await websocket.accept()

    session_id = UUID(await websocket.receive_text())

    session = await sessions.fetch_one(ctx, session_id)
    if isinstance(session, ServiceError):  # session does not exist
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    WEBSOCKETS[session["account_id"]].append(websocket)

    # tell the client they were accepted
    await websocket.send_json(
        {
            "message_type": ServerMessages.ACCEPTED,
            "data": {},
        }
    )

    try:
    while True:
        packet = Packet(**await websocket.receive_json())
            logger.debug("Handling packet: ", packet=packet)
        if packet.message_type == ClientMessages.SEND_CHAT_MESSAGE:
            data = SendChatMessage(**packet.data)

            target_websockets = WEBSOCKETS[data.target_account_id]
            for target_websocket in target_websockets:
                await target_websocket.send_json(
                    {
                        "message_type": ClientMessages.SEND_CHAT_MESSAGE,
                        "data": {
                            "message_content": data.message_content,
                            "sender_account_id": session["account_id"],
                        },
                    }
                )
        elif packet.message_type == ClientMessages.MARK_AS_READ:
            pass
        elif packet.message_type == ClientMessages.LOG_OUT:
            break
        pass
    except WebSocketDisconnect:
        pass
    else:
        await websocket.close()

    WEBSOCKETS[session["account_id"]].remove(websocket)

    data = await sessions.logout(ctx, session_id)
    if isinstance(data, ServiceError):
        # we won't raise an exception here, but this is weird
        logger.error("Failed to logout session", error=data)
    else:
        logger.info("Session logged out", data=data)
