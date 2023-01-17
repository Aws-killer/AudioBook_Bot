import ujson, aioaria2, emoji, os, pprint, re, asyncio


async def ubuntu_cleaner(folder):
    try:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        else:
            os.remove(folder)
        subprocess.call("apt-get clean", shell=True)
    except:
        pass


async def find_download(trigger, data):
    gid: str = data["params"][0]["gid"]
    uri: str = (await trigger.getFiles(gid))[0]["uris"][0]["uri"]
    path = uri.split("/")[-2]

    _download: DownloadDb = session.query(DownloadDb).filter_by(path=path).first()
    ujson.loads(_download.tl_data)
    return [
        uri,
        path,
        _download,
        ujson.loads(_download.status),
        ujson.loads(_download.tl_data),
    ]


async def download_pool():
    client: aioaria2.Aria2WebsocketClient = await aioaria2.Aria2WebsocketClient.new(
        "http://127.0.0.1:8070/jsonrpc",
        token="token",
        loads=ujson.loads,
        dumps=ujson.dumps,
    )
    # client.onDownloadComplete(on_download_complete)
    # client.onDownloadStart(on_download_start)
    return client


async def main():
    await init_database()
    _client = await download_pool()
    e = await asyncio.gather(
        *[
            _client.addUri(
                [link],
                options={"dir": f"./Downloads/Torrent"},
            )
            for link in [
                "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4",
                "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_640_3MG.mp4",
                "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_1920_18MG.mp4",
                "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_640_3MG.mp4",
            ]
        ]
    )
    print(e)
    await download_status(_client)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
