import datetime
from datetime import time

while self._running:

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f'第{i}次录制')

    print(f'录制url:{url}')
    houzhui = re.findall("\.\w+", url)[-1]
    print(f'文件后缀名：{houzhui}')

    filenameshort = now + houzhui
    filename = filepath + '/' + filenameshort  # os.path.join(filepath, filenameshort) #
    print(url)
    print("\r", " 分段录制视频中: ", filename, " 每录满: %d 分钟 存一个视频" % Splittime)
    # logger.info(f'{filename}录制')

    try:
        logger.info(f'{filename}开始录制')
        p = subprocess.check_output([
            ffmpeg_path, "-y",
            "-v", "verbose",
            "-rw_timeout", "10000000",  # 10s
            "-loglevel", "error",
            "-hide_banner",
            "-user_agent", get_random_ua(),
            "-protocol_whitelist", "rtmp,crypto,file,http,https,tcp,tls,udp,rtp",
            "-thread_queue_size", "1024",
            "-analyzeduration", "2147483647",
            "-probesize", "2147483647",
            "-fflags", "+discardcorrupt",
            "-i", url,
            "-bufsize", "5000k",
            "-map", "0",
            "-sn", "-dn",
            "-reconnect_delay_max", "30", "-reconnect_streamed", "-reconnect_at_eof",
            "-c:v", "copy",
            "-c:a", "copy",
            "-max_muxing_queue_size", "64",
            "-correct_ts_overflow", "1",
            "-f", "mpegts",
            # "-fs",str(Splitsizes),
            "-t", str(Splittimes),
            "{path}".format(path=filename),
        ], stderr=subprocess.STDOUT)

    except subprocess.TimeoutExpired as time_e:
        print(time_e)
        logger.info(time_e)
        time.sleep(5)
        continue

    except subprocess.CalledProcessError as call_e:
        print(call_e.output.decode(encoding="utf-8"))
        if 'NOT' in call_e.output.decode(encoding="utf-8").upper() or 'ERROR' in call_e.output.decode(
                encoding="utf-8").upper():
            logger.info('直播结束')
            logger.info(call_e.output.decode(encoding="utf-8"))
            # sched2.shutdown(wait=False)
            break
        time.sleep(5)
        continue
    except Exception as e:
        print(e)
        logger.info(e)
        if "error" in str(e):  # Unknown error
            logger.info('录制非正常结束2')
            # sched2.shutdown(wait=False)

        time.sleep(5)
        continue