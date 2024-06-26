import asyncio
from aiocoap import Context, Message
from aiocoap.numbers.codes import Code

async def main():
    context = await Context.create_client_context()

    while True:
        messaggio = input("Insert a message to send to the server: ")
        if messaggio.isdigit():
            numero = int(messaggio)
            messaggio_bytes = numero.to_bytes(length=1, byteorder='big')
        else:
            messaggio_bytes = messaggio.encode('utf-8')

        request = Message(code=Code.POST, payload=messaggio_bytes)
        request.set_request_uri('coap://localhost/input')
        
        response = await context.request(request).response
        print(f'Response: {response.code}')

if __name__ == "__main__":
    asyncio.run(main())
