import asyncio
import logging
from aiocoap import resource, Context, Message
from aiocoap.numbers.codes import Code

logging.basicConfig(level=logging.INFO)

class MyResource(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_post(self, request):
        try:
            payload = request.payload
            logging.info(f'Message received: {request}')
            logging.info(f'Payload (bytes): {payload}')
            logging.info(f'Payload (string): {payload.decode("utf-8")}')
            logging.info(f'Payload (hexadecimal): {payload.hex()}')
            logging.info(f'Payload (binary): {"".join(format(byte, "08b") for byte in payload)}')
            response = Message(code=Code.CHANGED)
            return response
        except Exception as e:
            logging.error(f"Error processing the request: {e}")
            return Message(code=Code.INTERNAL_SERVER_ERROR)

async def main():
    root = resource.Site()
    root.add_resource(('input',), MyResource())

    context = await Context.create_server_context(root, bind=('::1', 5683))  # IPv6 localhost
    logging.info("CoAP server listening on localhost")

    await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
