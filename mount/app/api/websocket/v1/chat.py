from uuid import UUID

from app.api.context import RequestContext
from app.common.errors import ServiceError
from app.models import ClientMessages
from app.models import Message
from app.models import ServerMessages
from app.models.chat_messages import SendChatMessage
from app.usecases import chat_messages
from app.usecases import sessions
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import WebSocket
from fastapi import WebSocketException

router = APIRouter()


# TODO: responses module


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    ctx: RequestContext = Depends(),
):
    await websocket.accept()

    session_id = UUID(await websocket.receive_text())

    session = await sessions.add_websocket(ctx, session_id, websocket)
    if isinstance(session, ServiceError):  # session does not exist
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # tell the client they were accepted
    await websocket.send_json(
        {
            "message_type": ServerMessages.ACCEPTED,
            "data": {},
        }
    )

    while True:
        raw_data = Message(**await websocket.receive_json())
        if raw_data.message_type == ClientMessages.SEND_CHAT_MESSAGE:
            data = SendChatMessage(**raw_data.data)

            # TODO: filtering params with fetch_one
            other_sessions = await sessions.fetch_many(
                ctx, account_id=data.target_account_id
            )
            if not other_sessions:
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

            target_session = other_sessions[0]

            await target_session["websocket"].send_json(
                {
                    "message_type": ClientMessages.SEND_CHAT_MESSAGE,
                    "data": {
                        "message_content": data.message_content,
                        "sender_account_id": session["account_id"],
                    },
                }
            )
        elif raw_data.message_type == ClientMessages.MARK_AS_READ:
            pass
        elif raw_data.message_type == ClientMessages.LOG_OUT:
            break

    await sessions.remove_websocket(ctx, session_id)
    await websocket.close()
