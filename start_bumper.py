#!/usr/bin/env python3

import bumper
import argparse
import asyncio

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--listen", type=str, default=None, help="start serving on address")
        parser.add_argument(
            "--announce", type=str, default=None, help="announce address to bots on checkin"
        )
        parser.add_argument("--debug", action="store_true", help="enable debug logs")
        args = parser.parse_args()

        if args.debug:
            bumper.bumper_debug = True

        if args.listen:
            bumper.bumper_listen = args.listen

        if args.announce:
            bumper.bumper_announce_ip = args.announce

        asyncio.run(bumper.start())

    except KeyboardInterrupt:
        bumper.bumperlog.info("Keyboard Interrupt!")
        pass

    except Exception as e:
        bumper.bumperlog.Exception(e)
        pass

    finally:
        asyncio.run(bumper.shutdown())
