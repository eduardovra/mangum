import json
from contextvars import ContextVar

from mangum.types import ASGIApp, Scope, Receive, Send, Message

from mangum.backends import WebSocket

# _scope = ContextVar("scope")


class WebSocketMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert (
            scope["type"] == "websocket"
        ), f"WebSocketMiddleware called with invalid scope type '{scope['type']}'"
        # _scope.set(scope.copy())
        scope["subscriptions"] = []

        print("oh")

        async def websocket_send(message: Message) -> None:
            print("haha")
            # nonlocal send

            if message["type"] == "websocket.send":
                text = message.get("text", "")
                if text:
                    _data = json.loads(text)
                    message_type = _data.get("type")
                    if message_type in ("broadcast.publish", "broadcast.subscribe"):
                        channel = _data["channel"]
                        body = _data.get("body")
                        message = {
                            "type": message_type,
                            "channel": channel,
                            "body": body,
                        }

                await send(message)

        await self.app(scope, receive, websocket_send)


# def subscribe(filename: str) -> str:
#     _s3_storage = s3_storage.get()
#     return _s3_storage.s3_url_for(filename)


# def publish(filename: str) -> str:
#     _s3_storage = s3_storage.get()
#     return _s3_storage.s3_url_for(filename)


# async def subscribe(self, channel: str) -> None:
#     await self._backend.subscribe(channel, connection_id=self.connection_id)
#     scope = _scope.get()
#     scope["extensions"]["websocket.broadcast"]["subscriptions"].append(channel)
#     await self.save_scope(scope)


# async def unsubscribe(self, channel: str) -> None:
#     await self._backend.unsubscribe(channel, connection_id=self.connection_id)
#     scope = _scope.get()
#     _scope["extensions"]["websocket.broadcast"]["subscriptions"].remove(channel)
#     await self.save_scope(scope)


# from mangum.types import ASGIApp, Scope, Receive, Send


# class BroadcastMiddleware:
#     def __init__(self, app: ASGIApp) -> None:
#         self.app = app

#     async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
#         if scope["type"] == "websocket":

#             if 'subscriptions'


#             headers = Headers(scope=scope)
#             if "gzip" in headers.get("Accept-Encoding", ""):
#                 responder = GZipResponder(self.app, self.minimum_size)
#                 await responder(scope, receive, send)
#                 return
#         await self.app(scope, receive, send)


# class GZipResponder:
#     def __init__(self, app: ASGIApp, minimum_size: int) -> None:
#         self.app = app
#         self.minimum_size = minimum_size
#         self.send = unattached_send  # type: Send
#         self.initial_message = {}  # type: Message
#         self.started = False
#         self.gzip_buffer = io.BytesIO()
#         self.gzip_file = gzip.GzipFile(mode="wb", fileobj=self.gzip_buffer)

#     async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
#         self.send = send
#         await self.app(scope, receive, self.send_with_gzip)

#     async def send_with_gzip(self, message: Message) -> None:
#         message_type = message["type"]
#         if message_type == "http.response.start":
#             # Don't send the initial message until we've determined how to
#             # modify the ougoging headers correctly.
#             self.initial_message = message
#         elif message_type == "http.response.body" and not self.started:
#             self.started = True
#             body = message.get("body", b"")
#             more_body = message.get("more_body", False)
#             if len(body) < self.minimum_size and not more_body:
#                 # Don't apply GZip to small outgoing responses.
#                 await self.send(self.initial_message)
#                 await self.send(message)
#             elif not more_body:
#                 # Standard GZip response.
#                 self.gzip_file.write(body)
#                 self.gzip_file.close()
#                 body = self.gzip_buffer.getvalue()

#                 headers = MutableHeaders(raw=self.initial_message["headers"])
#                 headers["Content-Encoding"] = "gzip"
#                 headers["Content-Length"] = str(len(body))
#                 headers.add_vary_header("Accept-Encoding")
#                 message["body"] = body

#                 await self.send(self.initial_message)
#                 await self.send(message)
#             else:
#                 # Initial body in streaming GZip response.
#                 headers = MutableHeaders(raw=self.initial_message["headers"])
#                 headers["Content-Encoding"] = "gzip"
#                 headers.add_vary_header("Accept-Encoding")
#                 del headers["Content-Length"]

#                 self.gzip_file.write(body)
#                 message["body"] = self.gzip_buffer.getvalue()
#                 self.gzip_buffer.seek(0)
#                 self.gzip_buffer.truncate()

#                 await self.send(self.initial_message)
#                 await self.send(message)

#         elif message_type == "http.response.body":
#             # Remaining body in streaming GZip response.
#             body = message.get("body", b"")
#             more_body = message.get("more_body", False)

#             self.gzip_file.write(body)
#             if not more_body:
#                 self.gzip_file.close()

#             message["body"] = self.gzip_buffer.getvalue()
#             self.gzip_buffer.seek(0)
#             self.gzip_buffer.truncate()

#             await self.send(message)