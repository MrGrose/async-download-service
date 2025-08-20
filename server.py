import asyncio
import logging
from pathlib import Path

import aiofiles
from aiohttp import web
from aiohttp.client_exceptions import ClientConnectionResetError

BASE_FOLDER = Path(__file__).parent
INTERVAL_SECS = 1

logger = logging.getLogger(__name__)


async def archive(request):
    headers = {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="photo_archive.zip"'
    }
    response = web.StreamResponse(headers=headers)

    folder_name = request.match_info.get('archive_hash', "")
    folder_path = BASE_FOLDER / f"test_photos/{folder_name}"

    if not folder_path.is_dir():
        raise web.HTTPNotFound(text="Архив не существует или был удален")

    await response.prepare(request)

    try:
        process = await asyncio.create_subprocess_exec(
            "zip", "-r", "-", f"test_photos/{folder_name}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        while True:
            chunk = await process.stdout.read(512000)
            if not chunk:
                break
            logger.info(f"Отправка фрагмента архива размером: {len(chunk)} байт")
            await asyncio.sleep(1)
            await response.write(chunk)

        await process.wait()
        await response.write_eof()

    except asyncio.CancelledError:
        logger.warning("Клиент разорвал соединение")
        raise
    except ClientConnectionResetError:
        logger.warning("Загрузка была прервана")
    except Exception as e:
        logger.error(f"Ошибка при отправке архива: {e}")
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r', encoding='utf-8') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)