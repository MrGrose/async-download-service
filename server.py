import argparse
import asyncio
import logging
from functools import partial
from pathlib import Path

import aiofiles
from aiohttp import web
from aiohttp.client_exceptions import ClientConnectionResetError

BASE_FOLDER = Path(__file__).parent
INTERVAL_SECS = 1

logger = logging.getLogger(__name__)


async def get_folder_path(request, path):
    folder_name = request.match_info["archive_hash"]
    folder_path = BASE_FOLDER / f"{path}/{folder_name}"
    if not folder_path.is_dir():
        raise web.HTTPNotFound(text="Архив не существует или был удален")
    return Path(folder_path.parent.name, folder_path.name)


async def stream_zip_archive(folder_path, delay, response):
    process = await asyncio.create_subprocess_exec(
        "zip", "-r", "-", folder_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        while chunk := await process.stdout.read(524288):
            logger.info(f"Отправка фрагмента архива размером: {len(chunk)} байт")
            await response.write(chunk)
            await asyncio.sleep(delay)
        await response.write_eof()
    finally:
        if process.returncode is None:
            process.kill()
        await process.wait()


async def archive(request, delay, path):
    headers = {
        "Content-Type": "application/zip",
        "Content-Disposition": "attachment; filename=photo_archive.zip"
    }
    folder_path = await get_folder_path(request, path)
    response = web.StreamResponse(headers=headers)
    await response.prepare(request)
    try:
        await stream_zip_archive(folder_path, delay, response)
    except asyncio.CancelledError:
        logger.warning("Загрузка была прервана")
        raise
    except ClientConnectionResetError:
        logger.warning("Разорвано соединение")
    except Exception as e:
        logger.error(f"Ошибка при отправке архива: {e}")
    return response


async def handle_index_page(request):
    async with aiofiles.open("index.html", mode="r", encoding="utf-8") as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type="text/html")


def create_parser():
    parser = argparse.ArgumentParser(description="Скрипт для загрузки фото архива")
    parser.add_argument("-l", action="store_false", help="Включение логирования")
    parser.add_argument("-d", type=int, default=1, help="Включение задержки в сек.")
    parser.add_argument("-p", type=str, default="photos/", help="Путь к каталогу с фотографиями")
    return parser


def main():
    parser = create_parser()
    parsed_args = parser.parse_args()
    log, delay, path = parsed_args.l, parsed_args.d, parsed_args.p

    if log:
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    app = web.Application()
    app.add_routes([
        web.get("/", handle_index_page),
        web.get("/archive/{archive_hash}/", partial(archive, delay=delay, path=path)),
    ])
    web.run_app(app)


if __name__ == "__main__":
    main()
