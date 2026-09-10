"""
SSE streaming helpers used by the chat streaming API routes.

SSE Format Standard:
data: <json>\n\n
"""

async def sse_stream_wrapper(generator):

    async for chunk in generator:
        yield f"data: {chunk}\n\n"

    yield "data: [DONE]\n\n"
